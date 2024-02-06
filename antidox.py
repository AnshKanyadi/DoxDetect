#under GNU GENERAL PUBLIC LICENSE (github provided)
import openai
import cv2
import easyocr
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
openai.api_key = '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'

# Create an OCR reader
reader = easyocr.Reader(['en'])

# Function to blur personal information in the image
def blur_personal_info(img):
    # Use EasyOCR to perform OCR and get bounding boxes
    results = reader.readtext(img)

    # Process each detected text region
    for result in results:
        bbox, text = result[0], result[1]
        bbox = [(int(point[0]), int(point[1])) for point in bbox]

        # Check if the text is personal information using GPT-3.5-turbo
        openai_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant, who decides if there is personal information like names, addresses, dates like 1/7/18 (example), city/location names, and other stuff like that in the text sent. If there is, respond yes."},
                {"role": "user", "content": text}
            ]
        )
        assistant_reply = openai_response['choices'][0]['message']['content']

        # If GPT-3.5-turbo indicates personal information, prompt for confirmation and blur the region
        if "yes" in assistant_reply.lower():
            user_input = messagebox.askyesno("Blur Confirmation", f"Do you want to blur this?: {text}")
            if user_input:
                ymin, ymax, xmin, xmax = (
                    min(point[1] for point in bbox),
                    max(point[1] for point in bbox),
                    min(point[0] for point in bbox),
                    max(point[0] for point in bbox),
                )
                roi = img[ymin:ymax, xmin:xmax]
                roi = cv2.GaussianBlur(roi, (31, 31), 0)  # Adjust kernel size for desired blur
                img[ymin:ymax, xmin:xmax] = roi

    return img

# Function to open file dialog and load image
def upload_image():
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        # Load and display the original image
        img = cv2.imread(file_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        original_image = Image.fromarray(img)
        tk_image_original = ImageTk.PhotoImage(original_image)
        label_original.config(image=tk_image_original)
        label_original.image = tk_image_original
        label_original_width = label_original.winfo_reqwidth()
        label_original.place(x=screen_width/2-label_original_width/2, y=200)

        # Blur the image in a separate thread
        threading.Thread(target=process_and_display_image, args=(file_path,)).start()

# Function to process and display the blurred image
def process_and_display_image(file_path):
    img = cv2.imread(file_path)
    img = blur_personal_info(img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    blurred_image = Image.fromarray(img)
    tk_image_blurred = ImageTk.PhotoImage(blurred_image)

    # Update the label_original with the blurred image
    label_original.config(image=tk_image_blurred)
    label_original.image = tk_image_blurred

# Create the main window
root = tk.Tk()
root.title("Image Blur App")

# Style for themed widgets
style = ttk.Style(root)
style.configure("TButton", padding=5, relief="flat", background="#4CAF50", foreground="white")
style.configure("TLabel", padding=5, font=('Helvetica', 12))

# Create and configure widgets
screen_width = root.winfo_screenwidth()

upload_button = tk.Button(root, text="Upload Image", command=upload_image)
upload_button.pack(pady=20)
button_width = upload_button.winfo_reqwidth()
upload_button.place(x=screen_width/2-button_width/2, y=100)

label = tk.Label(
    root,
    text="DoxDetect",
    font=("Arial", 30),  # Set the font
    fg="black",          # Set the text color
)
label.pack()
label_width = label.winfo_reqwidth()
label.place(x=screen_width/2-label_width/2, y=30)

label_original = tk.Label(root)
label_original.pack(pady=10)

# Center the window on the screen
root.eval('tk::PlaceWindow . center')

# Start Tkinter main loop
root.mainloop()