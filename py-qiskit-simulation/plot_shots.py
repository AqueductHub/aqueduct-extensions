import os
import matplotlib.pyplot as plt


if __name__ == "__main__":
    dpi = 96
    width = int(os.environ.get("width", "1000"))
    height = int(os.environ.get("height", "800"))
    plt.figure(figsize=(width / dpi, height / dpi), dpi=dpi)
    plt.plot([1, 2, 3])
    plt.savefig("x.png", dpi=dpi)
