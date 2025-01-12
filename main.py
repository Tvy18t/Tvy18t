import tkinter as tk
from tkinter import filedialog, messagebox
import qrcode
from PIL import Image, ImageTk
import cv2
import numpy as np
from pyzbar.pyzbar import decode

class QRCodeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("QR Code Generator & Reader")
        self.root.geometry("600x500")

        tk.Label(root, text="QR Code Generator & Reader", font=("Arial", 16, "bold"), fg="blue").pack(pady=10)

        generator_frame = tk.LabelFrame(root, text="Tạo QR Code", font=("Tahoma", 12))
        generator_frame.pack(fill="both", expand=True, padx=10, pady=10)

        tk.Label(generator_frame, text="Nhập văn bản:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.text_input = tk.Entry(generator_frame, width=40, font=("Tahoma", 12))
        self.text_input.grid(row=0, column=1, padx=5, pady=5)

        generate_btn = tk.Button(generator_frame, text="Tạo QR", command=self.generate_qr, bg="green", fg="white", font=("Tahoma", 12))
        generate_btn.grid(row=0, column=2, padx=5, pady=5)

        self.qr_label = tk.Label(generator_frame, text="", relief="sunken")
        self.qr_label.grid(row=1, column=0, columnspan=3, pady=10)

        save_btn = tk.Button(generator_frame, text="Lưu QR", command=self.save_qr, bg="blue", fg="white", font=("Tahoma", 12))
        save_btn.grid(row=2, column=1, pady=5)

        reader_frame = tk.LabelFrame(root, text="Đọc QR Code", font=("Tahoma", 12))
        reader_frame.pack(fill="both", expand=True, padx=10, pady=10)

        read_btn = tk.Button(reader_frame, text="Chọn hình ảnh để đọc QR", command=self.read_qr, bg="blue", fg="white", font=("Tahoma", 12))
        read_btn.pack(pady=5)

        camera_btn = tk.Button(reader_frame, text="Mở Camera", command=self.open_camera, bg="green", fg="white", font=("Tahoma", 12))
        camera_btn.pack(pady=5)

        self.result_label = tk.Label(reader_frame, text="", fg="green", wraplength=500, justify="center", font=("Tahoma", 12))
        self.result_label.pack(pady=5)

        clear_btn = tk.Button(root, text="Xóa", command=self.clear_app, bg="red", fg="white", font=("Tahoma", 12))
        clear_btn.pack(pady=10)

        self.generated_qr_path = "qr_code.png"

    def generate_qr(self):
        text = self.text_input.get()
        if not text.strip():
            messagebox.showwarning("Lỗi nhập liệu", "Vui lòng nhập văn bản để tạo QR code.")
            return

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(text.encode('utf-8'))
        qr.make(fit=True)

        qr_img = qr.make_image(fill_color="black", back_color="white")
        qr_img.save(self.generated_qr_path)

        img = Image.open(self.generated_qr_path)
        img = img.resize((150, 150), Image.LANCZOS)
        qr_photo = ImageTk.PhotoImage(img)

        self.qr_label.config(image=qr_photo)
        self.qr_label.image = qr_photo
        messagebox.showinfo("Thành công", "QR Code đã được tạo và lưu thành 'qr_code.png'.")

    def save_qr(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                img = Image.open(self.generated_qr_path)
                img.save(file_path)
                messagebox.showinfo("Thành công", f"QR Code đã được lưu tại {file_path}")
        except FileNotFoundError:
            messagebox.showerror("Lỗi", "Không có QR Code để lưu!")

    def read_qr(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if not file_path:
            return

        img = cv2.imread(file_path)
        decoded_objects = decode(img)

        if not decoded_objects:
            messagebox.showerror("Không tìm thấy QR Code", "Không tìm thấy QR code trong hình ảnh.")
            return

        for obj in decoded_objects:
            points = obj.polygon
            if len(points) > 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                points = hull
            points = np.array(points, dtype=int)

            cv2.polylines(img, [points], isClosed=True, color=(0, 255, 0), thickness=2)

            data = obj.data.decode("utf-8")

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_tk = ImageTk.PhotoImage(img_pil)

            top_img = tk.Toplevel(self.root)
            top_img.title("Ảnh với QR Code")
            label_img = tk.Label(top_img, image=img_tk)
            label_img.image = img_tk
            label_img.pack()

            top_text = tk.Toplevel(self.root)
            top_text.title("Nội dung QR Code")
            tk.Label(top_text, text=f"Nội dung QR Code: {data}", font=("Tahoma", 12), wraplength=400,
                     justify="center").pack(pady=20)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def open_camera(self):
        cap = None
        for i in range(3):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap.isOpened():
                print(f"Camera {i} is available")
                break
            else:
                cap.release()

        if cap is None or not cap.isOpened():
            messagebox.showerror("Lỗi Camera", "Không thể kết nối với camera.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            decoded_objects = decode(frame)
            for obj in decoded_objects:
                points = obj.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    points = hull
                points = np.array(points, dtype=int)

                cv2.polylines(frame, [points], isClosed=True, color=(0, 255, 0), thickness=2)

                data = obj.data.decode("utf-8")

                cv2.imshow("QR Code Scanner", frame)
                cv2.waitKey(1000)

                cap.release()
                cv2.destroyAllWindows()
                messagebox.showinfo("QR Code tìm thấy", f"Nội dung QR Code: {data}")
                return

            cv2.imshow("QR Code Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("QR Code Scanner", "Không tìm thấy QR Code.")

    def clear_app(self):
        self.text_input.delete(0, tk.END)
        self.qr_label.config(image="", text="")
        self.result_label.config(text="", fg="green")
        try:
            import os
            if os.path.exists(self.generated_qr_path):
                os.remove(self.generated_qr_path)
        except Exception as e:
            print(f"Error clearing QR Code: {e}")
        messagebox.showinfo("Xóa", "Ứng dụng đã được làm mới!")

if __name__ == "__main__":
    root = tk.Tk()
    app = QRCodeApp(root)
    root.mainloop()