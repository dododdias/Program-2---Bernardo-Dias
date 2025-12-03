from ga import run_genetic_algorithm


def main():
    best_individual, best_fitness = run_genetic_algorithm()

    print("\n=== FINAL RESULT ===")
    print(f"Best fitness in final generation: {best_fitness}")
    print("Best individual:")
    print(best_individual)


if __name__ == "__main__":
    main()
