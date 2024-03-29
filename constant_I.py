# general imports
from functools import lru_cache

# matplotlib imports
from matplotlib import rc
from matplotlib import pyplot as plt

# numpy imports
import numpy as np
from numpy.linalg import norm

# scipy imports
from scipy.integrate import fixed_quad
from scipy.linalg import hankel
from scipy.optimize  import root
from scipy.sparse import spdiags

# TODO: remove this
np.set_printoptions(linewidth=160)
rc('font', size=30)

# -----------------------------------------------------------------------------
# auxiliary functions
@np.vectorize
def quad(e,b,e_bar):
    return .5/e_bar+b/3.-b*(e/e_bar)**2.

# TODO: use the structure of A to simplify _alpha
@np.vectorize
def _alpha(i,j,M,N,b,e_bar,d_bar):
    y0 = 2.*d_bar*(i+M)-e_bar       # y_{i}
    y1 = y0+2.*d_bar                        # y_{i+1}               
    f = lambda m_til : quad(m_til-2.*d_bar*j,b,e_bar)       
    return fixed_quad(f,y0,y1)[0]

# -----------------------------------------------------------------------------
# uniform importance, non-uniform error message
class Message:

    def __init__(self,M=1,N=2,b=1.,tol=1.e-10):
        """
        Parameters 
        ----------
        M : int
            Number of knots per message
        N : int
            Number of messages
        b : float
            Error parameter

        """
        # primitives
        self.M = M
        self.N = N

        # error distribution
        self.b = b

        # knot spacing
        self.K = self.M*self.N
        self.e_bar = .5/self.N
        self.d_bar = .5/self.K

        # tolerance
        self.tol = tol

        # A matrix
        # TODO: what are the first columns of I and J?
        I = hankel(np.arange(-self.M,0),np.arange(-1,self.K))
        J = np.tile(np.arange(0,self.K+1),(self.M,1))
        self.A = _alpha(I[:,0],J[:,0],M,N,b,self.e_bar,self.d_bar)
        self.A = np.tile(self.A,(self.K+1,1)).T

        # B matrix      
        z = np.zeros(self.K)
        A_L = np.vstack((self.A[:,:-1],z))
        A_R = np.vstack((z,self.A[:,1:]))
        _data = A_L-A_R
        _diags = np.arange(0,-(self.M+1),-1)
        self.B = spdiags(_data,_diags,self.M+self.K,self.K)

        # c vector
        self.c = np.hstack((np.zeros(self.K),self.A[:,-1]))

        # solve for breakpoints
        def h_map(x):
            a = .5*(self.B.dot(x**2.)+self.c)/(self.B.dot(x)+self.c)
            return .5*self.B.T.dot(a**2.)/self.B.T.dot(a)

        x = np.linspace(0.,1.,self.K+2)
        x_new = x[1:-1]
        x_old = None
        it = 0
        while x_old is None or norm(x_new-x_old)>self.tol:
            it += 1
            x_old = x_new
            x_new = h_map(x_old)

        # TODO: setup with a maxiter
        self.x_sol = np.hstack((0,x_new,1))
        self.m_sol = np.linspace(0.,1.,self.K+2)
        print(str(it) + ' iterations')

    def plot_msg(self,fname,title=True):
        plt.plot(self.x_sol,self.m_sol,color="tab:blue",linewidth=4)
        plt.xlim([0,1])
        plt.ylim([-.1,1.1])
        plt.xlabel("state $q$")
        plt.ylabel("message $m$")
        if title:
            plt.title("$M$ = " + str(self.M) + 
                ", $N$ = " + str(self.N) + 
                " ($\\epsilon$ = " + str(.5/self.N) + 
                "), $b$ = " + str(self.b))
        plt.grid()
        plt.tight_layout()
        plt.savefig(fname)
        plt.close()

    def plot_err(self,fname,freq_min,freq_max,title=True,n_plot=100):
        e_plot = np.linspace(-self.e_bar,self.e_bar,n_plot)
        y_plot = quad(e_plot,self.b,self.e_bar)
        plt.plot(e_plot,y_plot,linewidth=4)
        plt.xlim([-1.5*self.e_bar,1.5*self.e_bar])
        plt.ylim([freq_min,freq_max])
        plt.xlabel("error $e$")
        plt.ylabel("frequency")
        plt.xticks([-self.e_bar,0.,self.e_bar])
        if title:
            plt.title("$M$ = " + str(self.M) + 
                ", $N$ = " + str(self.N) + 
                " ($\\epsilon$ = " + str(.5/self.N) + 
                "), $b$ = " + str(self.b))
        plt.grid()
        plt.tight_layout()
        plt.savefig(fname)
        plt.close()
