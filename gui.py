# gui.py
import tkinter as tk
from tkinter import ttk
from ga import run_genetic_algorithm, set_mutation_rate
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# lists to store history during execution
generations = []
best_vals = []
avg_vals = []
worst_vals = []


def main():
    global root, gen_label, best_label, avg_label, worst_label
    global mutation_scale, canvas, ax_best, ax_avg, ax_worst

    root = tk.Tk()
    root.title("GA Scheduler - Fitness Viewer")

    # Controls frame
    control_frame = ttk.Frame(root, padding=10)
    control_frame.pack(side=tk.TOP, fill=tk.X)

    # Mutation rate slider
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

    # Run button
    run_button = ttk.Button(control_frame, text="Run GA", command=start_ga)
    run_button.grid(row=0, column=2, padx=10)

    # Status labels
    gen_label = ttk.Label(control_frame, text="Generation: -")
    gen_label.grid(row=1, column=0, sticky="w")

    best_label = ttk.Label(control_frame, text="Best: -")
    best_label.grid(row=1, column=1, sticky="w")

    avg_label = ttk.Label(control_frame, text="Avg: -")
    avg_label.grid(row=1, column=2, sticky="w")

    worst_label = ttk.Label(control_frame, text="Worst: -")
    worst_label.grid(row=1, column=3, sticky="w")

    # Matplotlib figure
    fig = Figure(figsize=(6, 4))
    ax_best = fig.add_subplot(111)
    ax_best.set_xlabel("Generation")
    ax_best.set_ylabel("Fitness")
    ax_best.set_title("Fitness over Generations")

    # the three lines (best, avg, worst) share the same axis
    ax_avg = ax_best
    ax_worst = ax_best

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    root.mainloop()


def start_ga():
    """
    Called when the user clicks 'Run GA'.
    Resets the plot and runs the GA, calling the callback every generation.
    """
    # clear history
    generations.clear()
    best_vals.clear()
    avg_vals.clear()
    worst_vals.clear()

    # set global mutation_rate in GA
    rate = float(mutation_scale.get())
    set_mutation_rate(rate)

    # run GA; the callback will update the GUI
    run_genetic_algorithm(on_generation=on_generation_update)


def on_generation_update(gen, best, avg, worst, mutation_rate):
    """
    Callback function called by the GA at each generation.
    Updates the lists, labels, and plot.
    """
    generations.append(gen)
    best_vals.append(best)
    avg_vals.append(avg)
    worst_vals.append(worst)

    # update labels
    gen_label.config(text=f"Generation: {gen}")
    best_label.config(text=f"Best: {best:.4f}")
    avg_label.config(text=f"Avg: {avg:.4f}")
    worst_label.config(text=f"Worst: {worst:.4f}")

    # redraw the plot
    ax_best.clear()
    ax_best.set_xlabel("Generation")
    ax_best.set_ylabel("Fitness")
    ax_best.set_title("Fitness over Generations")

    ax_best.plot(generations, best_vals, label="Best")
    ax_best.plot(generations, avg_vals, label="Average")
    ax_best.plot(generations, worst_vals, label="Worst")
    ax_best.legend()

    canvas.draw()
    # force Tkinter to process pending events
    root.update_idletasks()


if __name__ == "__main__":
    main()

