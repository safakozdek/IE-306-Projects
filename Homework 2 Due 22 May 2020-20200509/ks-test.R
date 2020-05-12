file_path = 'C:\\Users\\ozdeks\\Desktop\\input.xls'
data <- read_xls(file_path)

day1 <- data['Day 1']
day2 <- data['Day 2']
unif_dist<-runif(488,0,400)
ks.test(day1, unif_dist)
ks.test(day2, unif_dist)
print('P-value is smaller than 0.05, the claim is rejected.')


