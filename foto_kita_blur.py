import cv2
import os
import time

# Import MediaPipe
try:
    import mediapipe as mp
    mp_hands = mp.solutions.hands
except (AttributeError, ModuleNotFoundError):
    from mediapipe.python.solutions import hands as mp_hands

# ==========================================
# 1. INISIALISASI AUDIO (Universal Player)
# ==========================================
class UniversalAudioPlayer:
    def __init__(self, file_path):
        self.file_path = file_path
        self.player_type = None
        self.player = None
        self.is_playing = False
        
        if not file_path or not os.path.exists(file_path):
            print("⚠️ File musik tidak ditemukan.")
            return

        # Windows Media Player (Mendukung .mp3, .m4a, .aac, .wav, dll.)
        try:
            import win32com.client
            self.player = win32com.client.Dispatch("WMPlayer.OCX")
            media = self.player.newMedia(self.file_path)
            self.player.currentPlaylist.appendItem(media)
            self.player.settings.setMode("loop", True)
            self.player.settings.volume = 100
            self.player_type = "wmp"
            print(f"✅ Audio dimuat: {os.path.basename(file_path)}")
            return
        except Exception:
            pass

        # Fallback ke Pygame
        try:
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(self.file_path)
            self.player_type = "pygame"
            print(f"✅ Audio dimuat via Pygame: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"⚠️ Gagal memuat musik: {e}")

    def play(self):
        if self.is_playing or not self.player_type:
            return
        try:
            if self.player_type == "wmp":
                self.player.controls.play()
            elif self.player_type == "pygame":
                import pygame
                pygame.mixer.music.play(-1)
            self.is_playing = True
        except Exception:
            pass

    def stop(self):
        if not self.is_playing or not self.player_type:
            return
        try:
            if self.player_type == "wmp":
                self.player.controls.stop()
            elif self.player_type == "pygame":
                import pygame
                pygame.mixer.music.stop()
            self.is_playing = False
        except Exception:
            pass


# Cari file audio secara otomatis di folder
folder_script = os.path.dirname(os.path.abspath(__file__))
daftar_file = os.listdir(folder_script)

file_audio = None
for nama in ["lagu.mp3.mp3", "lagu.mp3", "lagu.m4a", "lagu.wav"]:
    if nama in daftar_file:
        file_audio = os.path.join(folder_script, nama)
        break

if not file_audio:
    for f in daftar_file:
        if f.lower().endswith(('.mp3', '.m4a', '.wav', '.aac')):
            file_audio = os.path.join(folder_script, f)
            break

audio_player = UniversalAudioPlayer(file_audio)

# ==========================================
# 2. INISIALISASI MEDIAPIPE (ULTRA FAST LITE)
# ==========================================
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    model_complexity=0,           # 0 = Model teringan & paling cepat di dunia
    min_detection_confidence=0.4, # Cepat mendeteksi
    min_tracking_confidence=0.4
)

# Fungsi Deteksi Pose Peace (✌️)
def is_peace_gesture(landmarks):
    index_tip_up = landmarks[8].y < landmarks[6].y
    middle_tip_up = landmarks[12].y < landmarks[10].y
    ring_tip_down = landmarks[16].y > landmarks[14].y
    pinky_tip_down = landmarks[20].y > landmarks[18].y
    return index_tip_up and middle_tip_up and ring_tip_down and pinky_tip_down

# ==========================================
# 3. BUKA KAMERA DENGAN DIRECTSHOW (ANTI DELAY)
# ==========================================
# CAP_DSHOW menghilangkan delay buffering kamera di Windows
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Hanya 1 frame di memori (zero latency)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("\n🚀 PROGRAM SIAP (ZERO DELAY)! Tunjukkan pose ✌️ ke kamera.")
print("👉 Tekan 'q' atau 'ESC' untuk keluar.\n")

frame_count = 0
should_blur = False

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Kamera tidak terdeteksi.")
        break

    frame_count += 1
    # Flip cermin kamera
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    # Deteksi AI dijalankan dengan gambar mini (240x180) agar proses < 2 milidetik!
    if frame_count % 2 == 0:
        small_for_ai = cv2.resize(frame, (240, 180))
        rgb_small = cv2.cvtColor(small_for_ai, cv2.COLOR_BGR2RGB)
        rgb_small.flags.writeable = False
        results = hands.process(rgb_small)

        should_blur = False
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                if is_peace_gesture(hand_landmarks.landmark):
                    should_blur = True
                    break

    # ==========================================
    # 4. EFEK BLUR INSTAN (SUPER RESPONSIF)
    # ==========================================
    if should_blur:
        audio_player.play()

        # Fast Blur: perkecil -> blur -> perbesar
        small_frame = cv2.resize(frame, (w // 6, h // 6))
        blurred_small = cv2.GaussianBlur(small_frame, (19, 19), 0)
        frame = cv2.resize(blurred_small, (w, h), interpolation=cv2.INTER_LINEAR)

        # Teks Lirik Estetik
        teks = "foto kita blur ~"
        font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
        font_scale = 1.6
        thickness = 2
        
        text_size = cv2.getTextSize(teks, font, font_scale, thickness)[0]
        text_x = (w - text_size[0]) // 2
        text_y = h - 50

        # Bayangan hitam + teks putih
        cv2.putText(frame, teks, (text_x + 2, text_y + 2), font, font_scale, (30, 30, 30), thickness + 1, cv2.LINE_AA)
        cv2.putText(frame, teks, (text_x, text_y), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    else:
        audio_player.stop()

    # Tampilkan frame secara instan
    cv2.imshow("Tren TikTok - Foto Kita Blur", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or key == 27:
        break

# Bersihkan resource
audio_player.stop()
cap.release()
cv2.destroyAllWindows()