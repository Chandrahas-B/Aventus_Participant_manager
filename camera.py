import cv2

def open_camera():
    # Open the camera
    cap = cv2.VideoCapture(0)

    # Check if the camera was successfully opened
    if not cap.isOpened():
        print("Failed to open camera.")
        exit()

    data = []

    # Loop over frames from the camera
    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Check if a frame was successfully read
        if not ret:
            print("Failed to capture frame.")
            break

        # Scan for QR codes in the frame
        # item = scan_qrcodes(frame)
        
        # if item is None:
        #     # Display the frame with detected QR codes
        cv2.imshow("QR Code Scanner", frame)

        # else:
            # cv2.imshow("QR Code Scanner", frame)
        #     data.append(item)
        #     # Display the frame with detected QR codes

        # Wait for the 'q' key to exit or when 10 QR codes are detected
        if cv2.waitKey(1) & 0xFF == ord('q') or len(data) >= 10:
            break

    # Release the camera and close the OpenCV window
    cap.release()
    cv2.destroyAllWindows()

open_camera()