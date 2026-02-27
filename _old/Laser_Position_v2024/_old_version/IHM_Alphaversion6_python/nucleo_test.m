s = serialport('COM16', 115200);

writeline(s, 'P_0.1_0.1_100_!');
while(s.NumBytesAvailable == 0)
end
readline(s)
figure;
k = 0;
while(k < 1000)
    writeline(s, 'A_!');
    while(s.NumBytesAvailable == 0)
    end
    rLine = readline(s);
    rLineChar = char(rLine);
    stepC = sscanf(rLineChar, 'A_%lf_%lf_!');
    plot(stepC(1), stepC(2),'+b', 'MarkerSize',10, 'LineWidth',3); 
    hold on;
    k = k+1
end

writeline(s, 'P_0.1_0.1_100_!');
while(s.NumBytesAvailable == 0)
end
readline(s)


s
flush(s)
s

clear s;
