# -----------------------------------------------------------------------------------------------
import cv2
from ultralytics import YOLO
import sqlite3
from time import sleep
import os
# -----------------------------------------------------------------------------------------------

# -----------------------------------------------------------------------------------------------
DEBUG = True
# -----------------------------------------------------------------------------------------------
db_path = '/home/just/rokkhi.banglasolutions.com/client_software/proj_rokkhi_banglasolutions_com_db.sqlite3'
model = YOLO("yolov11n.pt")  # You can use yolov8s.pt for better accuracy
media_folder_path = '/home/just/rokkhi.banglasolutions.com/client_software/media/'
# -----------------------------------------------------------------------------------------------
CONFIDENCE_THRESHOLD = 0.33
FRAME_SKIP = 3
# -----------------------------------------------------------------------------------------------


# ***********************************************************************************************
def read_pending_detection_file_from_db():
    # -----------------------------------------------------------------------------------------------
    cur, conn = '', ''
    row_pk_db, video_path_db = 0, ''
    # -----------------------------------------------------------------------------------------------
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # -----------------------------------------------------------------------------------------------
        cur.execute("""
        SELECT id, video_path
        FROM app_devices_motionvideofromdevice 
        WHERE is_detection_applied = ? 
        LIMIT 1 
        """, (False,))
        # -----------------------------------------------------------------------------------------------
        no_of_rows = cur.fetchone()
        print('no_of_rows:', no_of_rows)
        # -----------------------------------------------------------------------------------------------
        if no_of_rows:
            row_pk_db = no_of_rows[0]
            video_path_db = no_of_rows[1]
        else:
            print('No more Pending Row :)')
            sleep(3)
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print('e1:read_pending_detection_file_from_db:', e)
    # -----------------------------------------------------------------------------------------------
    finally:
        try:
            cur.close()
            conn.close()
        except Exception as e:
            print('e2:read_pending_detection_file_from_db:', e)
    # -----------------------------------------------------------------------------------------------
    return row_pk_db, video_path_db
# ***********************************************************************************************


# ***********************************************************************************************
def update_motion_img_info_in_db(row_pk, motion_detected, motion_detected_frame_no, motion_img_path_for_db, person_detected, person_detected_frame_no, person_img_path_for_db):
    # -----------------------------------------------------------------------------------------------
    cur, conn, is_detection_applied = '', '', True
    # -----------------------------------------------------------------------------------------------
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # -----------------------------------------------------------------------------------------------
        cur.execute("""
        UPDATE app_devices_motionvideofromdevice 
        SET 
        is_detection_applied = ?, 
        is_motion_found = ?, 
        motion_found_frame_no = ?, 
        motion_found_frame_path = ?, 
        is_person_found = ?, 
        person_found_frame_no = ?, 
        person_found_frame_path = ? 
        WHERE 
        id = ? 
        """, (is_detection_applied, motion_detected, motion_detected_frame_no, motion_img_path_for_db, person_detected, person_detected_frame_no, person_img_path_for_db, row_pk))
        # -----------------------------------------------------------------------------------------------
        conn.commit()
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print('e1:update_motion_img_info_in_db:', e)
        conn.rollback()
    # -----------------------------------------------------------------------------------------------
    finally:
        try:
            cur.close()
            conn.close()
        except Exception as e:
            print('e2:update_motion_img_info_in_db:', e)
    # -----------------------------------------------------------------------------------------------
# ***********************************************************************************************


# ***********************************************************************************************
def delete_specific_row_from_db(row_id):
    # -----------------------------------------------------------------------------------------------
    cur, conn, is_detection_applied = '', '', True
    # -----------------------------------------------------------------------------------------------
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # -----------------------------------------------------------------------------------------------
        cur.execute("""DELETE FROM app_devices_motionvideofromdevice WHERE id = ? """, (row_id,))
        # -----------------------------------------------------------------------------------------------
        conn.commit()
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print('e1:delete_specific_row_from_db:', e)
        conn.rollback()
    # -----------------------------------------------------------------------------------------------
    finally:
        try:
            cur.close()
            conn.close()
        except Exception as e:
            print('e2:delete_specific_row_from_db:', e)
    # -----------------------------------------------------------------------------------------------
# ***********************************************************************************************


# ***********************************************************************************************
while True:
    try:
        # -----------------------------------------------------------------------------------------------
        sleep(1)
        # -----------------------------------------------------------------------------------------------
        row_pk, video_path = read_pending_detection_file_from_db()

        if DEBUG:
            print('row_pk, video_path: ', row_pk, video_path)
        # -----------------------------------------------------------------------------------------------
        motion_detected_frame_no = 0
        person_detected_frame_no = 0
        # -----------------------------------------------------------------------------------------------
        if row_pk and video_path:
            video_path_actual = media_folder_path + video_path
            cap = cv2.VideoCapture(video_path_actual)
            # -----------------------------------------------------------------------------------------------
            frame_id = 0
            prev_gray = None
            # -----------------------------------------------------------------------------------------------
            motion_detected = False
            motion_frame_saved = False
            motion_img_path_for_db = ''
            # -----------------------------------------------------------------------------------------------
            person_detected = False
            person_frame_saved = False
            person_img_path_for_db = ''
            # -----------------------------------------------------------------------------------------------
            while cap.isOpened():
                ret, frame = cap.read()
                # -----------------------------------------------------------------------------------------------
                if not ret:
                    break
                # -----------------------------------------------------------------------------------------------
                frame_id += 1

                if frame_id % FRAME_SKIP != 0:
                    continue
                # -----------------------------------------------------------------------------------------------
                # Resize and preprocess
                resized = cv2.resize(frame, (640, 480))
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                # -----------------------------------------------------------------------------------------------

                # -----------------------------------------------------------------------------------------------
                # --- Motion Detection ---
                if not motion_detected and prev_gray is not None:
                    diff = cv2.absdiff(prev_gray, gray)
                    thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                    thresh = cv2.dilate(thresh, None, iterations=2)
                    motion_area = cv2.countNonZero(thresh)
                    # -----------------------------------------------------------------------------------------------
                    if motion_area > 10000:
                        motion_detected = True
                        if DEBUG:
                            print(f"[MOTION] Motion detected at frame {frame_id}, area={motion_area}")
                        motion_detected_frame_no = frame_id
                        # -----------------------------------------------------------------------------------------------
                        if not motion_frame_saved:
                            path_without_ext = os.path.splitext(video_path)[0]
                            path_without_ext_actual = media_folder_path + path_without_ext + '_m.jpg'
                            cv2.imwrite(path_without_ext_actual, resized)
                            motion_frame_saved = True
                            # -----------------------------------------------------------------------------------------------
                            motion_img_path_for_db = path_without_ext + '_m.jpg'

                            if DEBUG:
                                print('path_without_ext: ', path_without_ext)
                                print('path_without_ext_actual: ', path_without_ext_actual)
                                print('motion_img_path_for_db: ', motion_img_path_for_db)
                # -----------------------------------------------------------------------------------------------
                prev_gray = gray.copy()
                # -----------------------------------------------------------------------------------------------

                # -----------------------------------------------------------------------------------------------
                # --- Person Detection ---
                if not person_detected:
                    results = model(resized, conf=CONFIDENCE_THRESHOLD, verbose=False)
                    # -----------------------------------------------------------------------------------------------
                    for r in results:
                        for box in r.boxes:
                            conf = float(box.conf[0])
                            cls = int(box.cls[0])
                            name = model.names[cls]
                            # -----------------------------------------------------------------------------------------------
                            if name == 'person' and conf >= CONFIDENCE_THRESHOLD:
                                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                                label = f"{name}: {conf:.2f}"
                                cv2.rectangle(resized, (x1, y1), (x2, y2), (0, 255, 0), 2)
                                cv2.putText(resized, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
                                # -----------------------------------------------------------------------------------------------
                                if not person_frame_saved:
                                    path_without_ext = os.path.splitext(video_path)[0]
                                    path_without_ext_actual = media_folder_path + path_without_ext + '_p.jpg'
                                    cv2.imwrite(path_without_ext_actual, resized)
                                    person_detected_frame_no = frame_id
                                    # -----------------------------------------------------------------------------------------------
                                    person_img_path_for_db = path_without_ext + '_p.jpg'
                                    # -----------------------------------------------------------------------------------------------
                                    person_detected = True
                                    person_frame_saved = True

                                    if DEBUG:
                                        print('path_without_ext: ', path_without_ext)
                                        print('path_without_ext_actual: ', path_without_ext_actual)
                                        print(f"[PERSON] Person detected at frame {frame_id}, confidence={conf:.2f}")
                                        print('person_img_path_for_db: ', person_img_path_for_db)
                # -----------------------------------------------------------------------------------------------
                # --- Exit when both are detected ---
                if motion_detected and person_detected:
                    if DEBUG:
                        print("[INFO] Both motion and person detected. Exiting...")

                    break
            # -----------------------------------------------------------------------------------------------
            cap.release()
            cv2.destroyAllWindows()
            # -----------------------------------------------------------------------------------------------
            # If Motion or Person is detected, Update Motion Image Info in DB
            if motion_detected or person_detected:
                update_motion_img_info_in_db(row_pk, motion_detected, motion_detected_frame_no, motion_img_path_for_db, person_detected, person_detected_frame_no, person_img_path_for_db)
            else:
                # DELETE the *.mp4 file and delete row from DB. This will save Server Storage
                try:
                    os.remove(video_path_actual)
                    delete_specific_row_from_db(row_pk)
                    # -----------------------------------------------------------------------------------------------
                    if DEBUG:
                        print(f"No Motion or Person detected, file {video_path_actual} DELETED")
                        print(f"Row {row_pk} DELETED")
                # -----------------------------------------------------------------------------------------------
                except Exception as e:
                    print('e:DBD: ', e)
    # -----------------------------------------------------------------------------------------------
    except Exception as e:
        print('e1:Exception in Main While Loop:', e)
# ***********************************************************************************************
