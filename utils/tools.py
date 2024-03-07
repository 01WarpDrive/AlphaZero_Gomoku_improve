import numpy as np

def winner_detect(board):
    m = board.last_move
    width = board.width
    height = board.height
    states = board.states
    player = states[m]
    h = m // width
    w = m % width
    # from left to right
    left, right = 0, width-1
    for i in range(w):
        # current = w - i - 1
        if states.get(m-i-1, -1) != player: 
            left = w - i
            break
    for i in range(width - w - 1):
        # current = w + i + 1
        if states.get(m+i+1, -1) != player: 
            right = w + i
            break
    # from bottom to top
    bottom, top = 0, height-1
    for i in range(h):
        # current = h - i - 1
        if states.get(m - (i+1)*width, -1) != player: 
            bottom = h - i
            break
    for i in range(height - h - 1):
        current = h + i + 1
        if states.get(m + (i+1)*width, -1) != player: 
            top = h + i
            break
    return left, right, bottom, top

def edge_protection(board):
    m = board.last_move
    width = board.width
    height = board.height
    states = board.states
    if not states: return -1
    player = states[m]
    h = m // width
    w = m % width

    if h == 0 or h == height - 1:
        left, right, _, _ = winner_detect(board)
        if right - left + 1 >= 3:
            potential = h*width+left-1
            if left - 1 >= 0 and states.get(potential, -1) == -1:
                return potential
            potential = h*width+right+1
            if right + 1 < width and states.get(potential, -1) == -1:
                return potential
    if w == 0 or w == width - 1:
        _, _, bottom, top = winner_detect(board)
        if top - bottom + 1 >= 3:
            potential = (bottom - 1)*width + w
            if bottom - 1 >= 0 and states.get(potential, -1) == -1:
                return potential
            potential = (top + 1)*width + w
            if top + 1 < height and states.get(potential, -1) == -1:
                return potential
    return -1


def softmax(x):
    """
    Perform softmax operations on the input vector to convert it into a probability distribution.
    x: (numpy.ndarray)
    probs: (numpy.ndarray)
    """
    probs = np.exp(x - np.max(x))
    probs /= np.sum(probs)
    return probs

