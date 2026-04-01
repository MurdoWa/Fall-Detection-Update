import numpy as np
from ImageDetection import *
from FileManager import *
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import time
import os


def main():
    """
    Main function to initialize Firebase, capture images, predict falls,
    and upload results.
    """

    # Ask user for number of cameras
    while True:
        try:
            cameraAmount = int(input("Enter number of cameras to use: "))
            if cameraAmount > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    # Firebase initialization
    cred = credentials.Certificate(
        'soc10101-fall-detection-firebase-adminsdk-fbsvc-601713d01f.json'
    )
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("Connected to Firebase successfully!")

    # Ask user for collection name
    collection_name = input(
        "Enter the Firestore collection name to push events to: "
    ).strip()

    if not collection_name:
        collection_name = "FallEvents"
        print(f"No name entered, defaulting to '{collection_name}'.")

    # Ask user whether to save or delete images after processing
    while True:
        save_choice = input("Save images after processing? (y/n): ").strip().lower()
        if save_choice in ("y", "n"):
            saveImages = save_choice == "y"
            break
        else:
            print("Please enter 'y' or 'n'.")

    threshold = 0.6
    saveLocation = "images/"
    predictions = [0] * cameraAmount

    last_state = None  # track last fall state to prevent spam uploads

    print("\nSystem running... Press CTRL+C to stop.\n")

    try:
        while True:

            # ⏱ Wait before next check
            time.sleep(1)

            # 📸 Capture + predict
            for i in range(cameraAmount):

                TakeIMG(saveLocation, "TEMPNAME.png", i)

                imgArray = ProcessImg(saveLocation + "TEMPNAME.png")

                predictions[i] = FallDetect(imgArray, threshold)

                renamed_file = RenameIMG(saveLocation, predictions[i], threshold)

                # 🧹 Delete image if not saving
                if not saveImages:
                    filepath = os.path.join(saveLocation, renamed_file)
                    if os.path.exists(filepath):
                        os.remove(filepath)

            # 🧠 Final decision
            fallPredFinal = MeanResults(predictions)

            timestamp = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
            fallDetected = bool(fallPredFinal < threshold)

            print(f"[{timestamp}] Fall: {fallDetected} (score={fallPredFinal})")

            # ☁️ Upload ONLY if state changes
            if fallDetected != last_state:
                db.collection(collection_name).document(timestamp).set({
                    "timestamp": timestamp,
                    "fall": fallDetected,
                    "prediction_score": float(fallPredFinal)
                })

                print("Uploaded to Firebase ✔")
                last_state = fallDetected

                if fallDetected:
                    print("🚨 Fall Detected!")
                else:
                    print("✅ No Fall Detected.")

    except KeyboardInterrupt:
        print("\nProgram stopped by user.")


if __name__ == "__main__":
    main()