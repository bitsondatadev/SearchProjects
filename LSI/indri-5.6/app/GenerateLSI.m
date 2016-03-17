load TFIDFMatrix.dat
M = spconvert(TFIDFMatrix);
k = input('Enter a k value:') %482
[U,S,V] = svds(M,k);
%dlmwrite('eigenvals.csv',svds(M, k));
L = U * inv(S);
V = V.';
save -ascii LSIMatrix.dat L
save -ascii VMatrix.dat V
