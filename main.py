# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import tkinter as tk
import numpy as np
from scipy.stats import t
from scipy.stats import f
from scipy.stats import norm
from tkinter import font
from tkinter import ttk
import math


def validate_int(new_value):
    if new_value.isdigit() or new_value == "":
        return True
    else:
        return False


class ResultGUI:
    def __init__(self, npMatrix, brojMjerenja, brojAlternativa):
        self.npMatrix = npMatrix
        self.broj_mjerenja = brojMjerenja
        self.broj_alternativa = brojAlternativa
        self.resultGui = tk.Tk()
        self.resultGui.geometry("500x500")
        self.resultGui.title("Rezultat Analize")
        self.resultGui.configure(background="#fff")
        self.calculate_Anova()
        self.labela_gresaka = tk.Label(self.resultGui, font=('Roboto', 10), bg="#fff",
                                       text=f"SSA={round(self.ssa, 2)} SSE={round(self.sse, 2)} SST={round(self.ssa + self.sse, 2)}")
        self.labela_f = tk.Label(self.resultGui, font=('Roboto', 10), bg="#fff",
                                 text=f"Izračunato F={round(self.fcalc, 2)} Tabularno F={round(self.ftab, 2)}")
        self.labela_gresaka.pack()
        self.labela_f.pack()
        self.canvas = tk.Canvas(self.resultGui)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.resultGui, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor='nw')

        labela2 = tk.Label(self.frame, text="KONTRASTI", font=('Roboto', 10), bg="#fff")
        labela2.pack()

        for i in range(len(self.afekti)):
            for j in range(i + 1, len(self.afekti)):
                self.calculate_Contrast(self.afekti[i], self.afekti[j], i, j)
        self.resultGui.mainloop()

    def calculate_Anova(self):
        self.srednje_vrijednosti_kolone = self.npMatrix.mean(axis=0)
        self.srednja_vrijednost = self.npMatrix.mean()
        self.afekti = self.npMatrix.mean(axis=0) - self.npMatrix.mean()
        self.ssa = np.sum((self.srednje_vrijednosti_kolone - self.srednja_vrijednost) ** 2) * len(self.npMatrix)
        self.sse = np.sum((self.npMatrix - self.srednje_vrijednosti_kolone) ** 2)
        self.df_e = self.npMatrix.size - self.srednje_vrijednosti_kolone.size  # k*(n-1)
        self.df_a = self.srednje_vrijednosti_kolone.size - 1  # k-1
        self.var_e = self.sse / self.df_e
        self.var_a = self.ssa / self.df_a
        self.fcalc = self.var_a / self.var_e
        alpha = 0.05
        self.ftab = f.ppf(1 - alpha, self.df_a, self.df_e)

    def calculate_Contrast(self, alfa1, alfa2, i, j):
        c = alfa1 - alfa2
        sc = math.sqrt(self.var_e) * (math.sqrt(2 / self.npMatrix.size))
        # self.raspodjela = 1.0
        if self.broj_mjerenja >= 30:
            self.raspodjela = norm.ppf(1)
        else:
            self.raspodjela = t.ppf(0.95, self.df_e)
        c1 = c - self.raspodjela * sc
        c2 = c + self.raspodjela * sc
        # breakpoint()
        resultic = "Poredimo " + str(i) + " i " + str(j)
        print(f"{c1} - {c2}")
        if (c1 < 0 < c2) or (c2 < 0 < c1):
            labela = tk.Label(self.frame, text=resultic + " Nema Razlike", font=('Roboto', 10), bg="#fff", )
            labela.pack()
        else:
            labela = tk.Label(self.frame, text=resultic + " Ima Razlike", font=('Roboto', 10), bg="#fff", )
            labela.pack()


class TableApp:
    def __init__(self, master):
        self.master = master
        self.master.geometry("500x500")
        self.master.title("Table App")
        self.frame = tk.Frame(self.master, width=250, height=250)
        self.frame.pack(side="top", fill="both", expand=True)
        self.canvas = tk.Canvas(self.frame, width=250, height=250, bg="#ffffff")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar_y = ttk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x = ttk.Scrollbar(self.master, orient="horizontal", command=self.canvas.xview)
        self.scrollbar_x.pack(side="top", fill="x", pady=5)
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        self.table_frame = tk.Frame(self.canvas)
        self.table_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.table_frame, anchor="nw")
        self.add_button = tk.Button(self.master, text="Generisi Tabelu", command=self.add_table_values)
        self.add_button.pack(pady=5)
        self.read_button = tk.Button(self.master, text="Izracunaj", command=self.read_table_values)
        self.read_button.pack(pady=5)
        self.rows_input = tk.Entry(self.master)
        self.columns_input = tk.Entry(self.master)
        self.rows_label = tk.Label(self.master, text="Broj Mjerenja:")
        self.columns_label = tk.Label(self.master, text="Broj Alternativa:")
        self.rows_label.pack()
        self.rows_input.pack()
        self.columns_label.pack()
        self.columns_input.pack()

    def add_table_values(self):
        self.rows = int(self.rows_input.get())
        self.columns = int(self.columns_input.get())
        self.table_entries = np.empty((self.rows, self.columns), dtype=object)

        # Add indexed rows
        for i in range(self.rows):
            row_label = tk.Label(self.table_frame, text="Mjerenje " + str(i + 1))
            row_label.grid(row=i + 1, column=0, padx=5, pady=5, sticky="w")

        # Add alternative columns
        for j in range(self.columns):
            col_label = tk.Label(self.table_frame, text="Alternativa " + str(j + 1))
            col_label.grid(row=0, column=j + 1, padx=5, pady=5, sticky="n")

        # Add table entries
        for i in range(self.rows):
            for j in range(self.columns):
                entry = tk.Entry(self.table_frame, width=10)
                entry.grid(row=i + 1, column=j + 1)
                self.table_entries[i, j] = entry

    def read_table_values(self):
        values = np.empty((self.table_entries.shape))
        for i in range(self.table_entries.shape[0]):
            for j in range(self.table_entries.shape[1]):
                values[i, j] = self.table_entries[i, j].get()
        ResultGUI(values, self.rows, self.columns)


if __name__ == "__main__":
    root = tk.Tk()
    app = TableApp(root)
    root.mainloop()
