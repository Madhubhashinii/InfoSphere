from flask import Flask, jsonify, render_template, request, redirect, url_for, session
from dao.db_connection import get_connection
import os, base64, io
import face_recognition
import numpy as np
from PIL import Image

app = Flask(__name__)
app.secret_key = 'infosphere_secret_key_2024'

PHOTOS_DIR = "static/storage/member_photos"
os.makedirs(PHOTOS_DIR, exist_ok=True)

# ── Helper: decode base64 → numpy RGB uint8 array ─────────────────────────────
def decode_image(image_b64):
    if "," in image_b64:
        image_b64 = image_b64.split(",", 1)[1]
    pil_img = Image.open(io.BytesIO(base64.b64decode(image_b64)))
    # Force clean RGB — handles RGBA, P, L etc from browser canvas
    if pil_img.mode != "RGB":
        bg = Image.new("RGB", pil_img.size, (255, 255, 255))
        bg.paste(pil_img.convert("RGB"))
        pil_img = bg
    # Upscale if too small for dlib
    w, h = pil_img.size
    if min(w, h) < 600:
        scale = 600 / min(w, h)
        pil_img = pil_img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return np.array(pil_img, dtype=np.uint8)

# ── Helper: get face encoding from numpy array ────────────────────────────────
def get_face_encoding(arr, label=""):
    locs = face_recognition.face_locations(arr, number_of_times_to_upsample=1, model="hog")
    print(f"  [{label}] shape={arr.shape} | faces found={len(locs)}")
    if not locs:
        return None
    encs = face_recognition.face_encodings(arr, known_face_locations=locs)
    return encs[0] if encs else None  # always returns numpy array, never list

# 1. NEW ENTRY POINT: The Starry Beginning Page
@app.route('/')
def index():
    # This now loads beginning.html first
    return render_template('beginning.html')

# 1.1 UPDATED WELCOME PAGE: The Login/Register buttons
@app.route('/welcome')
def welcome():
    # This renders frontView.html (the one with the "bloom" and buttons)
    return render_template('frontView.html')

# 2. REGISTER PAGE
@app.route('/register')
def register():
    return render_template('register.html')

# 3. SAVE FORM → GO TO SCAN
@app.route('/go_to_scan', methods=['POST'])
def go_to_scan():
    session['temp_user_data'] = {
        'full_name': request.form.get('full_name'),
        'email':     request.form.get('email'),
        'phone':     request.form.get('phone'),
        'address':   request.form.get('address'),
        'user_id':   request.form.get('user_id')
    }
    return redirect(url_for('facescan'))

# 4. FACE SCAN PAGE
@app.route('/facescan')
def facescan():
    if 'temp_user_data' not in session:
        return redirect(url_for('register'))
    return render_template('faceScan.html')

# 5. COMPLETE REGISTRATION
@app.route('/complete_registration', methods=['POST'])
def complete_registration():
    if 'temp_user_data' not in session:
        return jsonify({"status": "error", "message": "Session lost. Please restart."}), 400

    user_data = session['temp_user_data']
    image_b64 = request.json.get('image')

    try:
        arr = decode_image(image_b64)
        enc = get_face_encoding(arr, label="REGISTER")

        if enc is None:
            return jsonify({
                "status":  "error",
                "message": "No face detected. Face the camera directly with good lighting and try again."
            }), 400

        # Save photo
        db_path = os.path.join(PHOTOS_DIR, f"{user_data['user_id']}.jpg")
        Image.fromarray(arr).save(db_path, format="JPEG", quality=95)
        print(f"[REGISTER] Saved → {db_path}")

        # Save to DB
        db = get_connection()
        cur = db.cursor()
        cur.execute("""INSERT INTO members
                       (full_name, email, phone, address, user_id_code, face_encoding_path)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (user_data['full_name'], user_data['email'], user_data['phone'],
                     user_data['address'], user_data['user_id'], db_path))
        db.commit()
        cur.close(); db.close()

        session.pop('temp_user_data', None)
        return jsonify({"status": "success"})

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# 6. LOGIN PAGE
@app.route('/login')
def login():
    return render_template('checkin.html')

# 7. VERIFY FACE  ←  THE BUG WAS HERE: live_enc was being converted to list
@app.route('/verify_face', methods=['POST'])
def verify_face():
    image_b64 = request.json.get('image')

    try:
        # Get live encoding — stays as numpy array, never converted to list
        live_arr = decode_image(image_b64)
        live_enc = get_face_encoding(live_arr, label="LIVE")

        if live_enc is None:
            return jsonify({"status": "failed",
                            "message": "No face detected. Look directly at the camera."})

        # Load all registered members
        db = get_connection()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT user_id_code, full_name, face_encoding_path FROM members")
        members = cur.fetchall()
        cur.close(); db.close()

        best_match    = None
        best_distance = 1.0

        for member in members:
            path = member['face_encoding_path']
            if not os.path.exists(path):
                print(f"  [VERIFY] Missing file: {path}")
                continue

            reg_arr = decode_image_from_file(path)
            reg_enc = get_face_encoding(reg_arr, label=f"REG:{member['user_id_code']}")

            if reg_enc is None:
                print(f"  [VERIFY] No face in stored image for {member['user_id_code']}")
                continue

            # Both reg_enc and live_enc are numpy arrays here — subtraction works
            distance = face_recognition.face_distance([reg_enc], live_enc)[0]
            print(f"  [VERIFY] vs {member['user_id_code']} | distance={distance:.4f}")

            if distance < best_distance:
                best_distance = distance
                best_match    = member

        TOLERANCE = 0.6
        print(f"[VERIFY] Best={best_match['user_id_code'] if best_match else 'none'} | dist={best_distance:.4f}")

        if best_match and best_distance <= TOLERANCE:
            return jsonify({
                "status":  "success",
                "user_id": best_match['user_id_code'],
                "name":    best_match['full_name']
            })

        return jsonify({
            "status":  "failed",
            "message": f"Face not recognized (distance: {best_distance:.2f}). "
                       "Try better lighting and face the camera directly."
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

# ── Helper: load image from disk → numpy array (same pipeline as decode_image) -
def decode_image_from_file(path):
    pil_img = Image.open(path).convert("RGB")
    w, h = pil_img.size
    if min(w, h) < 600:
        scale = 600 / min(w, h)
        pil_img = pil_img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
    return np.array(pil_img, dtype=np.uint8)

# 8. HOME
@app.route('/home')
def home():
    return render_template('homeScreen.html')

# 9. VIEW MEMBERS
@app.route('/view_members')
def view_members():
    db  = get_connection()
    cur = db.cursor(dictionary=True)
    cur.execute('SELECT id, user_id_code, full_name, email, phone FROM members ORDER BY id DESC')
    members = cur.fetchall()
    cur.close(); db.close()
    return render_template('members.html', members=members)

# 10. DELETE MEMBER
@app.route('/delete_member/<int:member_id>', methods=['POST'])
def delete_member(member_id):
    try:
        db  = get_connection()
        cur = db.cursor(dictionary=True)
        # Get photo path before deleting
        cur.execute('SELECT face_encoding_path FROM members WHERE id = %s', (member_id,))
        row = cur.fetchone()
        # Delete from DB
        cur.execute('DELETE FROM members WHERE id = %s', (member_id,))
        db.commit()
        cur.close(); db.close()
        # Delete photo file from disk
        if row and os.path.exists(row['face_encoding_path']):
            os.remove(row['face_encoding_path'])
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
# 11. CATEGORIES    

@app.route('/category1')
def category1():
    return render_template('category1.html') # Fiction

@app.route('/category2')
def category2():
    return render_template('category2.html') # Academic

@app.route('/category3')
def category3():
    return render_template('category3.html') # Children

@app.route('/category4')
def category4():
    return render_template('category4.html') # Digital        

if __name__ == '__main__':
    app.run(debug=True)