import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
from PIL import Image, ImageTk
import cv2
from import_video import load_video, display_video
from compression import compress_video
from distortion_correction import correct_distortion
from speed_detection import detect_speeding
from save_annotated_segments import save_annotated_segments
from live_video import process_live_feed
from stitching import stitch_videos

class VideoProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Processing Application")

        self.video_path = None
        self.save_path = None
        self.speeding_segments = []

        # Set the main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(expand=True, fill="both")

        # Style for buttons and labels
        self.style = ttk.Style()
        self.style.configure('TButton', font=('Arial', 12))
        self.style.configure('TLabel', font=('Arial', 12))
        
        # Set background color
        root.configure(bg="#f0f0f0")
        self.main_frame.configure(style='TFrame')

        # Header label
        self.header_label = ttk.Label(self.main_frame, text="Speed Camera", font=('Arial', 20, 'bold'))
        self.header_label.pack(pady=20)

        # Create a frame for buttons
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=20)

        # Buttons
        self.load_icon = ImageTk.PhotoImage(Image.open("icons/open_file.png").resize((30, 30)))
        self.load_button = ttk.Button(self.button_frame, text=" Load Video", image=self.load_icon, compound=tk.LEFT, command=self.load_video)
        self.load_button.grid(row=0, column=0, padx=10, pady=10)

        self.correct_icon = ImageTk.PhotoImage(Image.open("icons/correct.png").resize((30, 30)))
        self.correct_button = ttk.Button(self.button_frame, text=" Correct Distortion", image=self.correct_icon, compound=tk.LEFT, command=self.correct_distortion, state=tk.DISABLED)
        self.correct_button.grid(row=0, column=1, padx=10, pady=10)

        self.speed_icon = ImageTk.PhotoImage(Image.open("icons/speed.png").resize((30, 30)))
        self.speed_button = ttk.Button(self.button_frame, text=" Detect Speeding", image=self.speed_icon, compound=tk.LEFT, command=self.detect_speeding, state=tk.DISABLED)
        self.speed_button.grid(row=0, column=2, padx=10, pady=10)

        self.compress_icon = ImageTk.PhotoImage(Image.open("icons/compress.png").resize((30, 30)))
        self.compress_button = ttk.Button(self.button_frame, text=" Compress Video", image=self.compress_icon, compound=tk.LEFT, command=self.compress_video, state=tk.DISABLED)
        self.compress_button.grid(row=0, column=3, padx=10, pady=10)

        self.save_icon = ImageTk.PhotoImage(Image.open("icons/save.png").resize((30, 30)))
        self.save_button = ttk.Button(self.button_frame, text=" Save Violations", image=self.save_icon, compound=tk.LEFT, command=self.save_violations, state=tk.DISABLED)
        self.save_button.grid(row=1, column=0, padx=10, pady=10)

        self.live_icon = ImageTk.PhotoImage(Image.open("icons/live.png").resize((30, 30)))
        self.live_button = ttk.Button(self.button_frame, text=" Start Live Feed", image=self.live_icon, compound=tk.LEFT, command=self.start_live_feed)
        self.live_button.grid(row=1, column=1, padx=10, pady=10)

        self.stitch_icon = ImageTk.PhotoImage(Image.open("icons/stitch.png").resize((30, 30)))
        self.stitch_button = ttk.Button(self.button_frame, text=" Stitch Videos", image=self.stitch_icon, compound=tk.LEFT, command=self.stitch_videos)
        self.stitch_button.grid(row=1, column=2, padx=10, pady=10)

        # Progress label
        self.progress_label = ttk.Label(self.main_frame, text="", style='TLabel')
        self.progress_label.pack(pady=20)

        # Live feed thread
        self.live_feed_thread = None
        self.live_feed_running = False

    def load_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv;*.flv;*.wmv;*.m4v")])
        if self.video_path:
            self.progress_label.config(text="Loading video...")
            self.load_button.config(state=tk.DISABLED)
            cap = load_video(self.video_path)
            if cap:
                display_video(cap)
                self.progress_label.config(text="Video loaded successfully!")
                self.correct_button.config(state=tk.NORMAL)
                self.speed_button.config(state=tk.NORMAL)
            else:
                messagebox.showerror("Error", "Failed to load video.")
            self.load_button.config(state=tk.NORMAL)

    def correct_distortion(self):
        if self.video_path:
            self.progress_label.config(text="Correcting distortion...")
            self.correct_button.config(state=tk.DISABLED)
            output_corrected_path = self.video_path.replace('.mp4', '_corrected.mp4')
            correct_distortion(self.video_path, output_corrected_path)
            self.progress_label.config(text="Distortion corrected successfully!")
            messagebox.showinfo("Processing Complete", "Distortion correction completed successfully!")
            self.correct_button.config(state=tk.NORMAL)
            self.video_path = output_corrected_path
            self.compress_button.config(state=tk.NORMAL)

    def compress_video(self):
        if self.video_path:
            self.progress_label.config(text="Compressing video...")
            self.compress_button.config(state=tk.DISABLED)
            output_compressed_path = self.video_path.replace('.mp4', '_compressed.mp4')
            compress_video(self.video_path, output_compressed_path)
            self.progress_label.config(text="Video compressed successfully!")
            messagebox.showinfo("Processing Complete", "Video compression completed successfully!")
            self.compress_button.config(state=tk.NORMAL)
            self.video_path = output_compressed_path

    def detect_speeding(self):
        if self.video_path:
            speed_limit = simpledialog.askfloat("Speed Limit", "Enter the speed limit (pixels per second):", parent=self.root)
            if speed_limit is not None:
                self.progress_label.config(text="Detecting speeding...")
                self.speed_button.config(state=tk.DISABLED)
                self.speeding_segments, categorized_movements, speeds = detect_speeding(self.video_path, speed_limit)
                self.progress_label.config(text="Speed detection completed!")
                messagebox.showinfo("Processing Complete", "Speed detection completed successfully!")
                self.speed_button.config(state=tk.NORMAL)
                self.save_button.config(state=tk.NORMAL)
                self.compress_button.config(state=tk.NORMAL)

    def save_violations(self):
        if self.video_path and self.speeding_segments:
            self.progress_label.config(text="Saving violations...")
            self.save_button.config(state=tk.DISABLED)
            self.save_path = filedialog.askdirectory(title="Select where to save violations")
            if self.save_path:
                save_annotated_segments(self.video_path, self.speeding_segments, self.save_path)
                self.progress_label.config(text="Violations saved successfully!")
                messagebox.showinfo("Processing Complete", "Violations saved successfully!")
                self.save_button.config(state=tk.NORMAL)

    def stitch_videos(self):
        self.progress_label.config(text="Stitching videos...")
        self.update_ui_state(disable_buttons=True)
        threading.Thread(target=self.process_stitch_videos).start()

    def process_stitch_videos(self):
        try:
            if self.video_path:
                video_paths = filedialog.askopenfilenames(
                    title="Select Video to Stitch",
                    filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv")]
                )
                if not video_paths or len(video_paths) < 1:
                    self.update_ui_state(disable_buttons=False)
                    self.root.after(0, self.progress_label.config, {'text': "Please select another video to stitch with the loaded video."})
                    return

                self.save_path = filedialog.askdirectory(title="Select where to save stitched video")
                if not self.save_path:
                    self.update_ui_state(disable_buttons=False)
                    self.root.after(0, self.progress_label.config, {'text': "No save location selected."})
                    return

                print(f"Stitching video with loaded video: {self.video_path} and {video_paths}")
                stitched_video_path = self.save_path + "/stitched_video.mp4"
                stitch_videos([self.video_path] + list(video_paths), stitched_video_path)
                self.root.after(0, self.progress_label.config, {'text': "Videos stitched successfully."})
                self.root.after(0, messagebox.showinfo, "Processing Complete", "Videos stitched successfully!")

            else:
                video_paths = filedialog.askopenfilenames(
                    title="Select Videos to Stitch",
                    filetypes=[("Video files", "*.mp4;*.avi;*.mov;*.mkv")]
                )
                if not video_paths or len(video_paths) < 2:
                    self.update_ui_state(disable_buttons=False)
                    self.root.after(0, self.progress_label.config, {'text': "Please select at least two videos for stitching."})
                    return

                self.save_path = filedialog.askdirectory(title="Select where to save stitched videos")
                if not self.save_path:
                    self.update_ui_state(disable_buttons=False)
                    self.root.after(0, self.progress_label.config, {'text': "No save location selected."})
                    return

                print(f"Stitching videos: {video_paths}")
                print(f"Save path: {self.save_path}")

                stitched_video_path = self.save_path + "/stitched_video.mp4"
                stitch_videos(video_paths, stitched_video_path)
                self.root.after(0, self.progress_label.config, {'text': "Videos stitched successfully."})
                self.root.after(0, messagebox.showinfo, "Processing Complete", "Videos stitched successfully!")
    
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Failed to stitch videos: {e}")
        finally:
            self.update_ui_state(disable_buttons=False)


    def start_live_feed(self):
        self.live_feed_running = True
        self.progress_label.config(text="Starting live feed...")
        self.live_button.config(state=tk.DISABLED)
        self.live_feed_thread = threading.Thread(target=self.process_live_feed)
        self.live_feed_thread.start()

    def process_live_feed(self):
        try:
            process_live_feed()
            self.root.after(0, self.progress_label.config, {'text': "Live feed processing completed."})
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Error", f"Failed to process live feed: {e}")
        finally:
            self.live_feed_running = False
            self.root.after(0, self.live_button.config, {'state': tk.NORMAL})

    def update_ui_state(self, disable_buttons):
        state = tk.DISABLED if disable_buttons else tk.NORMAL
        self.root.after(0, self.load_button.config, {'state': state})
        self.root.after(0, self.correct_button.config, {'state': state})
        self.root.after(0, self.speed_button.config, {'state': state})
        self.root.after(0, self.compress_button.config, {'state': state})
        self.root.after(0, self.save_button.config, {'state': state})
        self.root.after(0, self.live_button.config, {'state': state})
        self.root.after(0, self.stitch_button.config, {'state': state})

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoProcessingApp(root)
    root.mainloop()
