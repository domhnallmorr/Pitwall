import os 

import customtkinter

from pw_controller import pw_controller

def run(mode="normal"):
	if mode in ["normal"]:
		customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
		customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

		app = customtkinter.CTk()  # create CTk window like you do with the Tk window
		app.title("Pitwall V0.0.1")
	elif mode == "headless":
		app = None

	run_directory = os.path.dirname(os.path.join(os.path.abspath(__file__)))
	controller = pw_controller.Controller(app, run_directory, mode)

	if mode in ["normal"]:
		app.after(0, lambda:app.state("zoomed"))
		app.mainloop()
	
	elif mode == "headless":
		return controller

if __name__ == "__main__":
	run()