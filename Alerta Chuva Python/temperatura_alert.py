import customtkinter as ctk
import geocoder
import requests
import os
import threading
import time

location = geocoder.ip("me")
latitude, longitude = location.latlng
KEY = "64ed82577ced7f69cb1687f0ce536131"

response = requests.get(
    f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&lang=pt_br&units=metric&appid={KEY}"
)
data = response.json()
temperature = data["main"]["temp"]


class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Aviso ⚠️")
        root.geometry("300x200")
        root.resizable(False, False)

        self.weather_label = ctk.CTkLabel(
            root, text="Não foi encontrado o clima da sua região"
        )
        self.weather_label.pack(padx=10, pady=10)
        self.get_weather()
        self.root.after(60000, self.get_weather)

        self.shutdown_button = ctk.CTkButton(
            root, text="Desligar Computador", command=self.init_shutdown
        )
        self.shutdown_button.pack(padx=10, pady=15)

        self.cancel_button = ctk.CTkButton(
            root, text="Cancelar", command=self.cancel_shutdown, state="disabled"
        )
        self.cancel_button.pack(padx=10, pady=5)

        self.shutdown_cancelled = False
        self.shutdown_thread = None

    def get_weather(self):
        location = geocoder.ip("me")
        latitude, longitude = location.latlng
        KEY = "64ed82577ced7f69cb1687f0ce536131"

        url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&lang=pt_br&units=metric&appid={KEY}"
        response = requests.get(url)
        data = response.json()
        temperature = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]

        self.weather_label.configure(
            text=f"Temperatura: {temperature}°C\nClima: {weather_description.capitalize()}\n\n A temperatura recomendada é até 24°C\ne a máxima é 30°C"
        )
        self.root.after(60000, self.get_weather)

    def init_shutdown(self):
        self.shutdown_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")

        self.shutdown_thread = threading.Thread(target=self.countdown_shutdown)
        self.shutdown_thread.start()

    def countdown_shutdown(self):
        for i in range(30, -1, -1):
            if self.shutdown_cancelled:
                return
            self.shutdown_button.configure(text=f"Desligando em {i} segundos")
            time.sleep(1)

        if os.name == "nt":
            os.system("shutdown /s /f /t 0")

    def cancel_shutdown(self):
        self.shutdown_cancelled = True
        self.shutdown_thread.join()

        self.shutdown_button.configure(text="Desligar Computador", state="normal")
        self.cancel_button.configure(state="disabled")


if temperature >= 30:
    root = ctk.CTk()
    app = WeatherApp(root)
    root.mainloop()
