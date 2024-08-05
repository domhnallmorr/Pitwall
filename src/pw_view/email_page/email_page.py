import customtkinter


class EmailPage(customtkinter.CTkFrame):
	def __init__(self, master, view):
		super().__init__(master)

		self.view = view
		self.setup_labels()

	def setup_labels(self):
		customtkinter.CTkLabel(self, text="Email", font=self.view.page_title_font).grid(row=3, column=4, padx=self.view.padx*3, pady=self.view.pady, sticky="NW")

