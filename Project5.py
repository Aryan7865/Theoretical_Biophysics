# -*- coding: utf-8 -*-


import numpy as np
import scipy.stats
from scipy.stats import t, f


def lm_func(t,p):
    """

    Define model function used for nonlinear least squares curve-fitting.

    Parameters
    ----------
    t     : independent variable values (assumed to be error-free) (m x 1)
    p     : parameter values , n = 4 in these examples             (n x 1)

    Returns
    -------
    y_hat : curve-fit fctn evaluated at points t and with parameters p (m x 1)

    """

    y_hat = p[0,0]*np.exp(-p[1,0]*t) + p[2,0]*np.exp(p[3,0]*t) + p[4,0]*np.exp(-p[5, 0]*t)

    return y_hat


def lm_FD_J(t,p,y,dp):
    """

    Computes partial derivates (Jacobian) dy/dp via finite differences.

    Parameters
    ----------
    t  :     independent variables used as arg to lm_func (m x 1)
    p  :     current parameter values (n x 1)
    y  :     func(t,p,c) initialised by user before each call to lm_FD_J (m x 1)
    dp :     fractional increment of p for numerical derivatives
                - dp(j)>0 central differences calculated
                - dp(j)<0 one sided differences calculated
                - dp(j)=0 sets corresponding partials to zero; i.e. holds p(j) fixed

    Returns
    -------
    J :      Jacobian Matrix (n x m)

    """

    global func_calls

    # number of data points
    m = len(y)
    # number of parameters
    n = len(p)

    # initialize Jacobian to Zero
    ps=p
    J=np.zeros((m,n))
    del_=np.zeros((n,1))

    # START --- loop over all parameters
    for j in range(n):
        # parameter perturbation
        del_[j,0] = dp[j,0] * (1+abs(p[j,0]))
        # perturb parameter p(j)
        p[j,0]   = ps[j,0] + del_[j,0]

        if del_[j,0] != 0:
            y1 = lm_func(t,p)
            func_calls = func_calls + 1

            if dp[j,0] < 0:
                # backwards difference
                J[:,j] = (y1-y)/del_[j,0]
            else:
                # central difference, additional func call
                p[j,0] = ps[j,0] - del_[j]
                J[:,j] = (y1-lm_func(t,p)) / (2 * del_[j,0])
                func_calls = func_calls + 1

        # restore p(j)
        p[j,0]=ps[j,0]

    return J


def lm_Broyden_J(p_old,y_old,J,p,y):
    """
    Carry out a rank-1 update to the Jacobian matrix using Broyden's equation.

    Parameters
    ----------
    p_old :     previous set of parameters (n x 1)
    y_old :     model evaluation at previous set of parameters, y_hat(t,p_old) (m x 1)
    J     :     current version of the Jacobian matrix (m x n)
    p     :     current set of parameters (n x 1)
    y     :     model evaluation at current  set of parameters, y_hat(t,p) (m x 1)

    Returns
    -------
    J     :     rank-1 update to Jacobian Matrix J(i,j)=dy(i)/dp(j) (m x n)

    """

    h = p - p_old

    a = (np.array([y - y_old]).T - J@h)@h.T
    b = h.T@h

    # Broyden rank-1 update eq'n
    J = J + a/b

    return J

def lm_matx(t,p_old,y_old,dX2,J,p,y_dat,weight,dp):
    """
    Evaluate the linearized fitting matrix, JtWJ, and vector JtWdy, and
    calculate the Chi-squared error function, Chi_sq used by Levenberg-Marquardt
    algorithm (lm).

    Parameters
    ----------
    t      :     independent variables used as arg to lm_func (m x 1)
    p_old  :     previous parameter values (n x 1)
    y_old  :     previous model ... y_old = y_hat(t,p_old) (m x 1)
    dX2    :     previous change in Chi-squared criteria (1 x 1)
    J      :     Jacobian of model, y_hat, with respect to parameters, p (m x n)
    p      :     current parameter values (n x 1)
    y_dat  :     data to be fit by func(t,p,c) (m x 1)
    weight :     the weighting vector for least squares fit inverse of
                 the squared standard measurement errors
    dp     :     fractional increment of 'p' for numerical derivatives
                  - dp(j)>0 central differences calculated
                  - dp(j)<0 one sided differences calculated
                  - dp(j)=0 sets corresponding partials to zero; i.e. holds p(j) fixed

    Returns
    -------
    JtWJ   :     linearized Hessian matrix (inverse of covariance matrix) (n x n)
    JtWdy  :     linearized fitting vector (n x m)
    Chi_sq :     Chi-squared criteria: weighted sum of the squared residuals WSSR
    y_hat  :     model evaluated with parameters 'p' (m x 1)
    J :          Jacobian of model, y_hat, with respect to parameters, p (m x n)

    """

    global iteration,func_calls

    # number of parameters
    Npar   = len(p)

    # evaluate model using parameters 'p'
    y_hat = lm_func(t,p)

    func_calls = func_calls + 1

    if not np.remainder(iteration,2*Npar) or dX2 > 0:
        # finite difference
        J = lm_FD_J(t,p,y_hat,dp)
    else:
        # rank-1 update
        J = lm_Broyden_J(p_old,y_old,J,p,y_hat)

    # residual error between model and data
    delta_y = np.array([y_dat - y_hat]).T

    # Chi-squared error criteria
    Chi_sq = delta_y.T @ ( delta_y * weight )

    JtWJ  = J.T @ ( J * ( weight * np.ones((1,Npar)) ) )

    JtWdy = J.T @ ( weight * delta_y )


    return JtWJ,JtWdy,Chi_sq,y_hat,J


def lm(p,t,y_dat):
    """

    Levenberg Marquardt curve-fitting: minimize sum of weighted squared residuals

    Parameters
    ----------
    p : initial guess of parameter values (n x 1)
    t : independent variables (used as arg to lm_func) (m x 1)
    y_dat : data to be fit by func(t,p) (m x 1)

    Returns
    -------
    p       : least-squares optimal estimate of the parameter values
    redX2   : reduced Chi squared error criteria - should be close to 1
    sigma_p : asymptotic standard error of the parameters
    sigma_y : asymptotic standard error of the curve-fit
    corr_p  : correlation matrix of the parameters
    R_sq    : R-squared cofficient of multiple determination
    cvg_hst : convergence history (col 1: function calls, col 2: reduced chi-sq,
              col 3 through n: parameter values). Row number corresponds to
              iteration number.

    """

    global iteration, func_calls

    # iteration counter
    iteration  = 0
    # running count of function evaluations
    func_calls = 0

    # define eps (not available in python)
    eps = 5
    # number of parameters
    Npar   = len(p)
    # number of data points
    Npnt   = len(y_dat)
    # previous set of parameters
    p_old  = np.zeros((Npar,1))
    # previous model, y_old = y_hat(t,p_old)
    y_old  = np.zeros((Npnt,1))
    # a really big initial Chi-sq value
    X2     = 1e-3/eps
    # a really big initial Chi-sq value
    X2_old = 1e-3/eps
    # Jacobian matrix
    J      = np.zeros((Npnt,Npar))
    # statistical degrees of freedom
    DoF    = np.array([[Npnt - Npar + 1]])


    if len(t) != len(y_dat):
        print('The length of t must equal the length of y_dat!')
        X2 = 0
        corr_p = 0
        sigma_p = 0
        sigma_y = 0
        R_sq = 0

    # weights or a scalar weight value ( weight >= 0 )
    weight = 1/(y_dat.T@y_dat)
    # fractional increment of 'p' for numerical derivatives
    #dp = [-0.001]
    dp = [10**(-5)]
    # lower bounds for parameter values
    p_min = -100*abs(p)
    # upper bounds for parameter values
    p_max = 100*abs(p)

    MaxIter       = 76       # maximum number of iterations                       #change this value as per your dataset (ML iterations to reach tol)
    epsilon_1     = 1e-3        # convergence tolerance for gradient
    epsilon_2     = 8.30462e-06 # convergence tolerance for parameters              #change this as per your dataset (tol to exit value)
    epsilon_4     = 1e-1        # determines acceptance of a L-M step
    lambda_0      = 5        # initial value of damping paramter, lambda
    lambda_UP_fac = 5          # factor for increasing lambda
    lambda_DN_fac = 5           # factor for decreasing lambda
    Update_Type   = 1           # 1: Levenberg-Marquardt lambda update, 2: Quadratic update, 3: Nielsen's lambda update equations

    if len(dp) == 1:
        dp = dp*np.ones((Npar,1))

    idx   = np.arange(len(dp))  # indices of the parameters to be fit
    stop = 0                    # termination flag

    # identical weights vector
    if np.var(weight) == 0:
        weight = abs(weight)*np.ones((Npnt,1))
        print('Using uniform weights for error analysis')
    else:
        weight = abs(weight)

    # initialize Jacobian with finite difference calculation
    JtWJ,JtWdy,X2,y_hat,J = lm_matx(t,p_old,y_old,1,J,p,y_dat,weight,dp)
    if np.abs(JtWdy).max() < epsilon_1:
        print('*** Your Initial Guess is Extremely Close to Optimal ***')

    lambda_0 = np.atleast_2d([lambda_0])

    # Marquardt: init'l lambda
    if Update_Type == 1:
        lambda_  = lambda_0
    # Quadratic and Nielsen
    else:
        lambda_  = lambda_0 * max(np.diag(JtWJ))
        nu=2

    # previous value of X2
    X2_old = X2
    # initialize convergence history
    cvg_hst = np.ones((MaxIter,Npar+2))

    # -------- Start Main Loop ----------- #
    while not stop and iteration <= MaxIter:

        iteration = iteration + 1

        # incremental change in parameters
        # Marquardt

        h = np.linalg.solve((JtWJ + lambda_*np.diag(np.diag(JtWJ)) ), JtWdy)


        # update the [idx] elements
        p_try = p + h[idx]
        # apply constraints
        p_try = np.minimum(np.maximum(p_min,p_try),p_max)

        # residual error using p_try
        delta_y = np.array([y_dat - lm_func(t,p_try)]).T

        # floating point error; break
        if not all(np.isfinite(delta_y)):
          stop = 1
          break

        func_calls = func_calls + 1
        # Chi-squared error criteria
        X2_try = delta_y.T @ ( delta_y * weight )

        rho = np.matmul( h.T @ (lambda_ * h + JtWdy),np.linalg.inv(X2 - X2_try))
        # it IS significantly better
        if ( rho > epsilon_4 ):

            dX2 = X2 - X2_old
            X2_old = X2
            p_old = p
            y_old = y_hat
            # % accept p_try
            p = p_try

            JtWJ,JtWdy,X2,y_hat,J = lm_matx(t,p_old,y_old,dX2,J,p,y_dat,weight,dp)

            # % decrease lambda ==> Gauss-Newton method
            # % Levenberg
            if Update_Type == 1:
                lambda_ = max(lambda_/lambda_DN_fac,1.e-7)
            # % Quadratic
            elif Update_Type == 2:
                lambda_ = max( lambda_/(1 + alpha) , 1.e-7 )
            # % Nielsen
            else:
                lambda_ = lambda_*max( 1/3, 1-(2*rho-1)**3 )
                nu = 2

        # it IS NOT better
        else:
            # % do not accept p_try
            X2 = X2_old

            if not np.remainder(iteration,2*Npar):
                JtWJ,JtWdy,dX2,y_hat,J = lm_matx(t,p_old,y_old,-1,J,p,y_dat,weight,dp)

            # % increase lambda  ==> gradient descent method
            # % Levenberg

            lambda_ = min(lambda_*lambda_UP_fac,1.e7)


        # update convergence history ... save _reduced_ Chi-square
        cvg_hst[iteration-1,0] = func_calls
        cvg_hst[iteration-1,1] = X2/DoF

        for i in range(Npar):
            cvg_hst[iteration-1,i+2] = p.T[0][i]

        if ( max(abs(JtWdy)) < epsilon_1  and  iteration > 2 ):
          print('**** Convergence in r.h.s. ("JtWdy")  ****')
          stop = 1

        if ( max(abs(h)/(abs(p)+1e-12)) < epsilon_2  and  iteration > 2 ):
          print('**** Convergence in Parameters ****')
          stop = 1

        if ( iteration == MaxIter ):
          print('!! Maximum Number of Iterations Reached Without Convergence !!')
          stop = 1

        # --- End of Main Loop --- #
        # --- convergence achieved, find covariance and confidence intervals

    #  ---- Error Analysis ----
    #  recompute equal weights for paramter error analysis
    if np.var(weight) == 0:
        weight = DoF/(delta_y.T@delta_y) * np.ones((Npnt,1))

    # % reduced Chi-square
    redX2 = X2 / DoF

    JtWJ,JtWdy,X2,y_hat,J = lm_matx(t,p_old,y_old,-1,J,p,y_dat,weight,dp)

    # standard error of parameters
    covar_p = np.linalg.inv(JtWJ)
    inv = covar_p
    sigma_p = np.sqrt(np.diag(covar_p))
    error_p = sigma_p/p

    # standard error of the fit
    sigma_y = np.zeros((Npnt,1))
    for i in range(Npnt):
        sigma_y[i,0] = J[i,:] @ covar_p @ J[i,:].T

    sigma_y = np.sqrt(sigma_y)

    # parameter correlation matrix
    corr_p = covar_p / [sigma_p@sigma_p.T]

    # coefficient of multiple determination
    R_sq = np.correlate(y_dat, y_hat)
    R_sq = 0

    # convergence history
    cvg_hst = cvg_hst[:iteration,:]

    print('\nLM fitting results:')
    for i in range(Npar):
        print('----------------------------- ')
        print('parameter      = p%i' %(i+1))
        print('fitted value   = %0.4f' % p[i,0])
        print('standard error = %0.2f %%' % error_p[i,0])

    return p,redX2,sigma_p,sigma_y,corr_p,R_sq,cvg_hst, JtWJ, inv

import numpy as np
import matplotlib.pyplot as plt

def main(x,y,p_init):
    """

    Main function for performing Levenberg-Marquardt curve fitting.

    Parameters
    ----------
    x           : x-values of input data (m x 1), must be 2D array
    y           : y-values of input data (m x 1), must be 2D array
    p_init      : initial guess of parameters values (n x 1), must be 2D array
                  n = 4 in this example

    Returns
    -------
    p       : least-squares optimal estimate of the parameter values
    Chi_sq  : reduced Chi squared error criteria - should be close to 1
    sigma_p : asymptotic standard error of the parameters
    sigma_y : asymptotic standard error of the curve-fit
    corr    : correlation matrix of the parameters
    R_sq    : R-squared cofficient of multiple determination
    cvg_hst : convergence history (col 1: function calls, col 2: reduced chi-sq,
              col 3 through n: parameter values). Row number corresponds to
              iteration number.

    """


    # minimize sum of weighted squared residuals with L-M least squares analysis
    p_fit,Chi_sq,sigma_p,sigma_y,corr,R_sq,cvg_hst, JtWJ, inv = lm(p_init,x,y)

    return p_fit,Chi_sq,sigma_p,sigma_y,corr,R_sq,cvg_hst, JtWJ, inv

if __name__ == '__main__':

    # flag for making noisy test data
    make_test_data = False

    x = np.array([0.0, 0.02, 0.04, 0.06, 0.08, 0.1, 0.12, 0.14, 0.16, 0.18, 0.2, 0.22, 0.24, 0.26, 0.28, 0.3, 0.32, 0.34, 0.36, 0.38, 0.4, 0.42, 0.44, 0.46, 0.48, 0.5, 0.52, 0.54, 0.56, 0.58, 0.6, 0.62, 0.64, 0.66, 0.68, 0.7, 0.72, 0.74, 0.76, 0.78, 0.8, 0.82, 0.84, 0.86, 0.88, 0.9, 0.92, 0.94, 0.96, 0.98, 1.0, 1.02, 1.04, 1.06, 1.08, 1.1, 1.12, 1.14, 1.16, 1.18, 1.2, 1.22, 1.24, 1.26, 1.28, 1.3, 1.32, 1.34, 1.36, 1.38, 1.4, 1.42, 1.44, 1.46, 1.48, 1.5, 1.52, 1.54, 1.56, 1.58, 1.6, 1.62, 1.64, 1.66, 1.68, 1.7, 1.72, 1.74, 1.76, 1.78, 1.8, 1.82, 1.84, 1.86, 1.88, 1.9, 1.92, 1.94, 1.96, 1.98, 2.0, 2.02, 2.04, 2.06, 2.08, 2.1, 2.12, 2.14, 2.16, 2.18, 2.2, 2.22, 2.24, 2.26, 2.28, 2.3, 2.32, 2.34, 2.36, 2.38, 2.4, 2.42, 2.44, 2.46, 2.48, 2.5, 2.52, 2.54, 2.56, 2.58, 2.6, 2.62, 2.64, 2.66, 2.68, 2.7, 2.72, 2.74, 2.76, 2.78, 2.8, 2.82, 2.84, 2.86, 2.88, 2.9, 2.92, 2.94, 2.96, 2.98])
    y = np.array([8.83495, 8.93995, 8.79963, 8.74592, 8.60279, 8.55959, 8.39714, 8.48836, 8.30669, 8.18984, 8.23806, 8.14314, 8.27182, 8.06469, 7.87759, 7.93303, 7.60783, 7.70537, 7.73949, 7.62501, 7.60763, 7.56328, 7.45224, 7.21446, 7.34391, 7.25029, 7.30344, 7.27458, 7.06239, 7.15777, 7.02408, 6.9052, 6.7224, 6.61736, 6.66216, 6.73185, 6.65275, 6.40096, 6.53693, 6.50425, 6.28483, 6.20103, 6.33008, 6.20527, 6.06906, 6.06673, 6.02343, 6.23313, 6.07637, 5.77906, 5.83179, 5.73937, 5.74065, 5.62095, 5.82376, 5.7641, 5.72798, 5.66125, 5.53929, 5.34524, 5.35613, 5.4151, 5.46055, 5.19746, 5.48782, 5.22529, 5.22759, 5.06215, 5.10408, 5.19137, 5.17659, 4.93481, 4.94715, 4.96005, 4.89191, 4.81703, 4.85079, 4.68142, 4.65036, 4.51725, 4.69305, 4.57623, 4.5986, 4.58899, 4.61747, 4.42485, 4.32722, 4.4074, 4.22968, 4.33492, 4.32131, 4.19774, 4.32111, 4.40177, 4.16635, 4.14304, 3.94273, 4.03299, 3.93099, 4.0596,4.07135, 3.85163, 4.00523, 4.02336, 4.10443, 3.66252, 3.80528, 3.94834, 3.75637, 3.67035, 3.68917, 3.65159, 3.46119, 3.6114, 3.50229, 3.32806, 3.48662, 3.59046, 3.44973, 3.57768, 3.49351, 3.42112, 3.39601, 3.32952, 3.20713, 3.35853, 3.21302, 3.31671, 3.20436, 3.29151, 3.14428, 3.22103, 3.06689, 2.94693, 3.13882, 3.0227, 2.98073, 2.98372, 2.9455, 2.96104, 3.23768, 2.9289, 2.91961, 2.82069, 3.04194, 2.82005, 2.76146, 2.91165, 2.84249, 2.72275])

    # jtj_ind = (3,1)
    # jtjinv_ind = (3, 6)
    # cov_ind = (4, 1)

    alpha = 0.0450367 # change this as per your dataset

    p_init = np.array([[0.1, 1, 1, 1, 1, 1]]).T
    p_fit,Chi_sq,sigma_p,sigma_y,corr,R_sq,cvg_hst,JtWJ, inv = main(x,y,p_init)
    xypoint = []
    for i in range(len(x)):
        xypoint.append((x[i], y[i]))
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    y_hat = lm_func(x, p_fit)
    ax1.scatter(x, y_hat, c='b', marker='s')
    ax1.scatter(x, y, c='r', marker='o')
    plt.show()

delta_y = np.array([y - lm_func(x,p_fit)]).T
sse = 0
for i in delta_y:
  sse += i**2
p = 6
n = 150
sigma_sq = sse / (n - p)
cov_beta = inv*sigma_sq
cov_beta

p_fit_low = np.zeros((6,1))
p_fit_high = np.zeros((6,1))
for i in range(6):
  p_fit_low[i, 0] = p_fit[i, 0] - abs(t.ppf(alpha/2, 144)) * np.sqrt(cov_beta[i, i])
  p_fit_high[i, 0] = p_fit[i, 0] + abs(t.ppf(alpha/2, 144)) * np.sqrt(cov_beta[i, i])
# p_fit_low
# p_fit_high

JtWJ[0, 4] #put index of JTJ matrix

inv[2, 0] #put index of JTJ Inverse matrix

cov_beta[1,3] #put index of cov beta matrix

p_fit_low[1] #put index of Kth parameter (if low is asked)

