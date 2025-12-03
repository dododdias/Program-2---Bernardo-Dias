# gui.py
import tkinter as tk
from tkinter import ttk
from ga import run_genetic_algorithm, set_mutation_rate
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# listas para guardar o histórico durante a execução
generations = []
best_vals = []
avg_vals = []
worst_vals = []

def main():
    global root, gen_label, best_label, avg_label, worst_label
    global mutation_scale, canvas, ax_best, ax_avg, ax_worst

    root = tk.Tk()
    root.title("GA Scheduler - Fitness Viewer")

    # Frame de controles
    control_frame = ttk.Frame(root, padding=10)
    control_frame.pack(side=tk.TOP, fill=tk.X)

    # Slider de mutation rate
    ttk.Label(control_frame, text="Mutation rate:").grid(row=0, column=0, sticky="w")
    mutation_scale = ttk.Scale(
        control_frame,
        from_=0.001,
        to=0.1,
        value=0.01,
        orient="horizontal",
        length=200,
    )
    mutation_scale.grid(row=0, column=1, padx=5)

    # Botão Run
    run_button = ttk.Button(control_frame, text="Run GA", command=start_ga)
    run_button.grid(row=0, column=2, padx=10)

    # Labels de status
    gen_label = ttk.Label(control_frame, text="Generation: -")
    gen_label.grid(row=1, column=0, sticky="w")

    best_label = ttk.Label(control_frame, text="Best: -")
    best_label.grid(row=1, column=1, sticky="w")

    avg_label = ttk.Label(control_frame, text="Avg: -")
    avg_label.grid(row=1, column=2, sticky="w")

    worst_label = ttk.Label(control_frame, text="Worst: -")
    worst_label.grid(row=1, column=3, sticky="w")

    # Figura do Matplotlib
    fig = Figure(figsize=(6, 4))
    ax_best = fig.add_subplot(111)
    ax_best.set_xlabel("Generation")
    ax_best.set_ylabel("Fitness")
    ax_best.set_title("Fitness over Generations")

    # as três linhas (best, avg, worst) vão compartilhar o mesmo eixo
    ax_avg = ax_best
    ax_worst = ax_best

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    root.mainloop()


def start_ga():
    """
    Chamado quando o usuário clica em 'Run GA'.
    Reseta o gráfico e roda o GA chamando o callback a cada geração.
    """
    # zera histórico
    generations.clear()
    best_vals.clear()
    avg_vals.clear()
    worst_vals.clear()

    # seta mutation_rate global no GA
    rate = float(mutation_scale.get())
    set_mutation_rate(rate)

    # roda o GA; o callback vai atualizando a GUI
    run_genetic_algorithm(on_generation=on_generation_update)


def on_generation_update(gen, best, avg, worst, mutation_rate):
    """
    Função callback chamada a cada geração pelo GA.
    Atualiza listas, labels e o gráfico.
    """
    generations.append(gen)
    best_vals.append(best)
    avg_vals.append(avg)
    worst_vals.append(worst)

    # atualiza labels
    gen_label.config(text=f"Generation: {gen}")
    best_label.config(text=f"Best: {best:.4f}")
    avg_label.config(text=f"Avg: {avg:.4f}")
    worst_label.config(text=f"Worst: {worst:.4f}")

    # redesenha o gráfico
    ax_best.clear()
    ax_best.set_xlabel("Generation")
    ax_best.set_ylabel("Fitness")
    ax_best.set_title("Fitness over Generations")

    ax_best.plot(generations, best_vals, label="Best")
    ax_best.plot(generations, avg_vals, label="Average")
    ax_best.plot(generations, worst_vals, label="Worst")
    ax_best.legend()

    canvas.draw()
    # força o Tkinter a processar eventos pendentes (mantém a GUI responsiva)
    root.update_idletasks()


if __name__ == "__main__":
    main()
