s = serialport('COM20', 115200);

flush(s);

writeline(s, 'P_1_1_1000_!');
while(s.NumBytesAvailable == 0)
end
readline(s)

writeline(s, 'M_1_1_!');
while(s.NumBytesAvailable == 0)
end
readline(s)

writeline(s, 'A_!');
k = 0;
while(k < 10)
    while(s.NumBytesAvailable == 0)
    end
    readline(s)
    k = k+1
end

k = 0;
while(k < 10)
    writeline(s, 'M_1_1_!');
    while(s.NumBytesAvailable == 0)
    end
    readline(s)
    k = k+1
end

writeline(s, 'P_1_1_1000_!');
while(s.NumBytesAvailable == 0)
end
readline(s)

s

clear s;