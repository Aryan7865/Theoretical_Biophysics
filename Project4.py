# -*- coding: utf-8 -*-


tau_t = [0.244724, 0.260536, 0.275872, 0.290804, 0.305404, 0.319716, 0.333782, 0.347617, 0.361265, 0.37474, 0.388071, 0.401271, 0.414356, 0.427341, 0.440238, 0.453064, 0.465817, 0.478499, 0.491151, 0.503746, 0.516312, 0.528863, 0.541371, 0.553879, 0.566373, 0.578853, 0.591346, 0.603826, 0.616319, 0.628842, 0.641365, 0.653916, 0.666482, 0.679077, 0.691715, 0.704367, 0.717077, 0.729816, 0.742613, 0.755438, 0.768336, 0.781277, 0.794276, 0.807332, 0.820446, 0.833632, 0.846891, 0.860221, 0.873624, 0.887099, 0.90066, 0.914308, 0.928042, 0.941878, 0.9558, 0.969837, 0.983961, 0.998201, 1.01256, 1.02703, 1.04161, 1.05634, 1.0712, 1.08619, 1.10134, 1.11665, 1.13211, 1.14775, 1.16358, 1.17961, 1.19584, 1.21228, 1.22897, 1.24593, 1.26317, 1.28069, 1.29856, 1.31679, 1.3354, 1.35447, 1.37402, 1.39413, 1.41487, 1.4363, 1.45855, 1.48175, 1.50606];
rin=0.09:0.01:0.95;
dt=1e-5;
Ps=1;
errorbest = 1e5;
vbest=0;
hillbest=0;
wbest=0;
sigmabest=0;
mubest=0;
value = 1; %change this to according to the value given P = 1 or M=2....
calc = 1;

for hill=1:1:10
    disp(hill);
   for mu=0.001:0.001:0.01
        for v=0.0001:0.0001:0.001
            for w=0.1:0.1:1
                for sigma=1:1:10
                    rt = responsetimeneg(v,w,mu,sigma,hill,dt,1e-6,rin,value);
                    error = sum((rt(:,2) - tau_t').^2);
                    if error < errorbest
                       errorbest=error;
                       vbest=v;
                       hillbest=hill;
                       wbest=w;
                       sigmabest=sigma;
                       mubest=mu;

                    end

                end
            end
        end
    end
end

 disp([vbest,wbest,mubest,sigmabest,hillbest]);

 function ps = psteadystate(mu,hillc,tol)
     tolc = 1e5; ps = 0.1;
     while tolc > tol
         pt = ps;
         ps = ps + (mu-ps*(mu+ps^hillc)) / (mu+(hillc)*ps^(hillc - 1));
         tolc = abs(pt-ps);
     end
 end

function ret = responsetimeneg(v,w,mu,sigma,hill,dt,tol,r,optmp)
    ps = psteadystate(mu,hill,tol); xs = ps/(mu+ps^hill); ms = 1-xs;
    ret = zeros(length(r),2); ret(:,1) = r;
    xt = 0; mt = 0; pt = 0; tau = 0; stat = 0; q = 1;
    while stat == 0
        xt = xt + (((1-xt)*(pt^hill)-mu*xt)/v)*dt;
        mt = mt + (1-xt-mt)*dt/w;
        pt = pt + (mt-pt-sigma*((1-xt)*(pt^hill)-mu*xt))*dt;
        tau = tau + dt;
        if optmp == 1
            if pt >= r(q)*ps
                ret(q,2) = tau/log(2);
                q = q + 1;
                if q > length(r)
                    stat = 1;
                end
            end
        elseif optmp == 2
           if mt >= r(q)*ms
                ret(q,2) = tau/log(2);
                q = q + 1;
                if q > length(r)
                    stat = 1;
                end
            end
        end
    end
end
