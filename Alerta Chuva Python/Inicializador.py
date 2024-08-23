import customtkinter as ctk
import geocoder
import requests
import os
import threading
import time
from time import strftime, localtime


class WeatherApp:
    def __init__(self, root):
        # Titulo
        self.root = root
        self.root.title("Bem vindo")
        root.geometry("300x385")
        root.resizable(False, False)

        # Horário Atual
        self.hora_atual = ctk.CTkLabel(
            root, text="Carregando...", font=("calibri", 60, "bold")
        )
        self.hora_atual.pack(padx=10)
        self.atualizar_horas()

        # Data de hoje
        self.dia_atual = ctk.CTkLabel(
            root, text="Carregando...", font=("calibri", 15, "bold")
        )
        self.dia_atual.pack(padx=10)
        self.atualizar_dia()

        # Temperatura Atual
        self.weather_label = ctk.CTkLabel(
            root, text="Não foi encontrado o clima da sua região"
        )
        self.weather_label.pack(padx=10, pady=10)
        self.get_weather()
        self.root.after(60000, self.get_weather)  # Atualiza a cada Minuto

        # Aviso(caso necessário)
        self.aviso_label = ctk.CTkLabel(root)
        self.aviso()
        self.aviso_label.pack(padx=10, pady=10)

        # Botão de Desligar o Computador
        self.shutdown_button = ctk.CTkButton(
            root, text="Desligar Computador", command=self.init_shutdown
        )
        self.shutdown_button.pack(padx=10, pady=15)

        # Botão de Cancelar Desligar o Computador
        self.cancel_button = ctk.CTkButton(
            root, text="Cancelar", command=self.cancel_shutdown, state="disabled"
        )
        self.cancel_button.pack(padx=10, pady=5)

        self.shutdown_cancelled = False
        self.shutdown_thread = None

    def atualizar_horas(self):
        # Atualiza as horas a cada segundo e de acordo com a hora
        hora = strftime("%H:%M:%S")
        if 18 >= int(strftime("%H")) >= 23:
            self.hora_atual.configure(text=f"🌑\n{hora}")
        elif 0 <= int(strftime("%H")) <= 5:
            self.hora_atual.configure(text=f"💤\n{hora}")
        elif 6 <= int(strftime("%H")) <= 11:
            self.hora_atual.configure(text=f"🏃‍♂️\n{hora}")
        else:
            self.hora_atual.configure(text=f"☀️\n{hora}")

        self.root.after(1000, self.atualizar_horas)

    def atualizar_dia(self):
        # Mostra o dia de Hoje
        data = localtime()
        dia_semana = data.tm_wday
        ano = data.tm_year
        mes = data.tm_mon
        dia = data.tm_mday

        dia_semana_text = [
            "Segunda-feira",
            "Terça-feira",
            "Quarta-feira",
            "Quinta-feira",
            "Sexta-feira",
            "Sábado",
            "Domingo",
        ]

        self.dia_atual.configure(
            text=f"{dia}/{mes}/{ano}, {dia_semana_text[dia_semana]}"
        )

        self.root.after(1000, self.atualizar_dia)

    def get_weather(self):
        # Pega a minha localização atual e minha chave de acesso para a API
        location = geocoder.ip("me")
        latitude, longitude = location.latlng
        KEY = "64ed82577ced7f69cb1687f0ce536131"

        # Pesquisa no site e pega os dados de clima
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&lang=pt_br&units=metric&appid={KEY}"
        response = requests.get(url)
        data = response.json()
        temperature = data["main"]["temp"]
        weather_description = data["weather"][0]["description"]

        # Troca as informações para as atuais
        self.weather_label.configure(
            text=f"Temperatura: {temperature}°C\nClima: {weather_description.capitalize()}"
        )
        self.root.after(60000, self.get_weather)  # Atualiza a cada Minuto

    def aviso(self, temperature=None):
        if temperature is None:
            temperature = self.get_temperature()

        aviso_text = ""
        if (7 >= int(strftime("%H")) >= 0) or (23 == int(strftime("%H"))):
            aviso_text = "Aviso:\nDesligue o seu computador e vá dormir."
        elif temperature >= 30:
            aviso_text = "Aviso:\nA Temperatura superou o limite (30ºC)\ne é recomendado desligar."
        elif temperature >= 30 and (
            (7 >= int(strftime("%H")) >= 0) or (23 == int(strftime("%H")))
        ):
            aviso_text = "Aviso:\nA Temperatura (acima de 30ºC) e o Horário\nnão são recomendados."

        self.aviso_label.configure(text=aviso_text)
        self.root.after(1000, self.aviso)  # Atualiza a cada Minuto

    def get_temperature(self):
        location = geocoder.ip("me")
        latitude, longitude = location.latlng
        KEY = "64ed82577ced7f69cb1687f0ce536131"

        url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&lang=pt_br&units=metric&appid={KEY}"
        response = requests.get(url)
        data = response.json()
        return data["main"]["temp"]

    def init_shutdown(self):
        # Muda o estado dos botões
        self.shutdown_button.configure(state="disabled")
        self.cancel_button.configure(state="normal")

        self.shutdown_thread = threading.Thread(
            target=self.countdown_shutdown
        )  # Declata que o texto vai ser definido pela função
        self.shutdown_thread.start()  # Chama a função contagem regressiva(countdown)

    def countdown_shutdown(self):
        # Contagem regressiva padrão
        for i in range(30, -1, -1):
            if self.shutdown_cancelled:
                return
            self.shutdown_button.configure(text=f"Desligando em {i} segundos")
            time.sleep(1)

        # Desligar computador após a contagem
        if os.name == "nt":
            os.system("shutdown /s /f /t 0")

    def cancel_shutdown(self):
        # Como a função vai ser Verdadeira, ela cancela o loop da contagem regressiva
        self.shutdown_cancelled = True
        self.shutdown_thread.join()

        # Volta o estado padrão dos botões
        self.shutdown_button.configure(text="Desligar Computador", state="normal")
        self.cancel_button.configure(state="disabled")


if __name__ == "__main__":
    root = ctk.CTk()
    app = WeatherApp(root)
    root.mainloop()
