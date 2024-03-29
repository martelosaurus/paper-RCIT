import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import gaussian_kde
from scipy.integrate import solve_ivp

def _djia():

    # parameters
    n_plt = 100
    r_min = -.05
    r_max = .05
    m0 = .5

    # load DJIA data
    m = pd.read_csv("data/DJA.csv",skiprows=4)

    # --------------------------------------------------------------------------
    # kde
    p = m["DJIA"]
    r = p.to_numpy()/p.shift().to_numpy()-1.
    r = r[1:]
    f = gaussian_kde(r)
    r_plt_up = np.linspace(0,r_max,n_plt)
    r_plt_dn = np.linspace(0,r_min,n_plt)
    m_p = lambda t, y: f.pdf(t)**(1/3)
    sol_up = solve_ivp(m_p,(0,r_max),[m0],t_eval=r_plt_up)
    sol_dn = solve_ivp(m_p,(0,r_min),[m0],t_eval=r_plt_dn)
    r_plt = np.hstack([r_plt_dn,r_plt_up])
    r_plt.sort()

    # --------------------------------------------------------------------------
    # plot
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.fill_between(r_plt, f.pdf(r_plt), alpha=0.5)
    ax1.plot(r_plt,f.pdf(r_plt),'-')
    ax2.plot(r_plt_up,sol_up.y[0],'-k',linewidth=2)
    ax2.plot(r_plt_dn,sol_dn.y[0],'-k',linewidth=2)
    ax1.set_xlabel("Previous trading day DJIA returns")
    ax1.set_ylabel("Density")
    ax2.set_ylabel("Message")
    xt = np.r_[-4:5:1]
    ax1.set_xticks(xt/100)
    ax1.set_xticklabels([str(t)+"%" for t in xt])
    ax2.legend(["Implied Message Function"],loc="upper left")
    plt.savefig("djia_plot.pdf")
