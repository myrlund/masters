import matplotlib.pyplot as plt

def plot_feature(conn, feature, values, log=False):
    """Do a simple histogram to determine distribution."""
    
    # Yay, mutability
    if log:
        values = map(lambda x: math.log(x), filter(lambda x: x, values))
    
    plt.title("Feature: %s" % feature)
    plt.hist(values, bins=100)
    plt.show()
