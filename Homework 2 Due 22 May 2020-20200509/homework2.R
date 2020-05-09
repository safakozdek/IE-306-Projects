library("xlsx")
std_error <- function(x) sd(x)/sqrt(length(x))
pexp_interval <- function(a,b,rate) pexp(b, rate) - pexp(a, rate)


data <- read.xlsx("input.xls", sheetIndex = 1)

day1 <- data[['Day.1']]
day2 <- data[['Day.2']]

#               1           2                3         4             5          6          7          8
day1_stats <- c(mean(day1), std_error(day1), sd(day1), median(day1), min(day1), max(day1), sum(day1), length(day1))
day2_stats <- c(mean(day2), std_error(day2), sd(day2), median(day2), min(day2), max(day2), sum(day2), length(day2))

day1_hist <- hist(day1, breaks=seq(0,ceiling(day1_stats[6])+10,by=10))
day2_hist <- hist(day2, breaks=seq(0,ceiling(day2_stats[6])+10,by=10))


# Chi Square Test for day 1
observed <- day1_hist$counts
expected <- vector(,length(observed))

index <- 1
for (i in seq(10,length(observed)*10,10)){
    expected[index] <- pexp_interval(i-10, i, 1/day1_stats[1])
    index <- index+1
}
expected <- expected*day1_stats[8]
chisq_stat <- sum((observed-expected)**2/expected)
p_value = 1-pchisq(chisq_stat,df=length(expected)-2)


print(chisq_stat)
print(p_value)
