import numpy as np
import matplotlib.pyplot as plt

def read_txt_file(file_path):
    """
    读取训练日志文件的所有行
    输出: list of lines
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def parse_data(lines, tag):
    """
    解析每行中指定tag对应的数据
    输出: list of data
    """
    values = []
    for line in lines:
        # 解析每行数据
        parts = line.split(',')
        for part in parts:
            if tag in part:
                # 提取loss值
                value = float(part.split(':')[1])
                values.append(value)
    return values

def plot_with_fit(lines, tag, title, ylabel, xlabel='Epoch', fit_dig=12, save_path=None):
    """
    绘制、输出并保存可视化图表
    """
    loss_values = parse_data(lines, tag)
    # 生成 x 值（0, 1, 2, ...）
    x_values = np.arange(len(loss_values))

    # 多项式拟合，这里使用二次多项式
    coefficients = np.polyfit(x_values, loss_values, fit_dig)
    polynomial = np.poly1d(coefficients)
    y_fit = polynomial(x_values)

    plt.figure()  # 创建一个新的图形窗口
    # 绘制原始数据和拟合曲线
    plt.plot(x_values, loss_values, marker='', linestyle='-', label='Original Data')
    plt.plot(x_values, y_fit, marker='', linestyle='-', label='Fit Curve')

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    if save_path:
        plt.savefig(save_path)  # 保存图形到指定路径
    plt.show()
    plt.close()

if __name__ == "__main__":
    train_process_path = "./model/train_process.txt"
    evaluate_path = "./model/evaluate.txt"
    batch_path = "./model/batch.txt"
    save_dir = "./visualize/"
    lines = read_txt_file(train_process_path)

    plot_with_fit(lines, 'loss', 'Loss Curve with Fit', 'Loss', save_path=save_dir + 'loss_plot.png')
    plot_with_fit(lines, 'entropy', 'entropy Curve with Fit', 'policy entropy', save_path=save_dir + 'entropy_plot.png')
    plot_with_fit(lines, 'lr_multiplier', 'lr_multiplier Curve with Fit', 'learning rate factor', save_path=save_dir + 'lr_plot.png')

