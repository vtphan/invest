
#------------------------------------------------------------------------------------------
def buy_the_dip(expected_market_loss, threshold_to_buy, buy_amount, price_per_share):
	original_price = price_per_share
	drop = 0
	capital_spent = 0
	total_shares = 0
	market_value = 0
	i = 0
	print('Buy ${} at first {} drop. Add ${} at each {} drop. Each share costs ${}.'.format(
			buy_amount, threshold_to_buy, buy_amount, threshold_to_buy, price_per_share))
	print('i\tCash  \tLoss\tDrop\tPPS\tShares \tMarket value')
	while price_per_share >= (1-expected_market_loss) * original_price:
		price_per_share *= (1-threshold_to_buy)
		shares = buy_amount / price_per_share
		total_shares += shares
		capital_spent += buy_amount
		market_value = price_per_share * total_shares
		drop += threshold_to_buy
		print('{}\t${}K\t{}\t{}\t${}\t{}\t${}'.format(
			i, 
			round(capital_spent/1000,1), 
			round(1-market_value/capital_spent,2),
			round(drop,2),
			round(price_per_share,2), 
			round(total_shares,2), 
			round(market_value,2),
		))
		buy_amount += buy_amount
		i += 1
	return capital_spent, total_shares, price_per_share, market_value, threshold_to_buy

#------------------------------------------------------------------------------------------
def buy_at_bottom(amount, price_per_share):
	shares = amount / price_per_share
	print('Buy at bottom:', 'shares =',round(shares,2), 'market value =', amount)

#------------------------------------------------------------------------------------------

if __name__ == '__main__':
	import sys
	if len(sys.argv) != 3:
		print('Summary:\n\tCalculate different scenarios for buying at each drop in the market.')
		print('Usage:\n\tpython', sys.argv[0], 'expected_market_loss buy_amount')
		print('Example:\n\tpython', sys.argv[0], '0.30 500\n')
		sys.exit(1)
	expected_market_loss = float(sys.argv[1])
	buy_amount = float(sys.argv[2])
	price_per_share = 1000
	for r in [0.03, 0.04, 0.05, 0.06, 0.07]:
		capital_spent, shares, pps, mv, t = buy_the_dip(
			expected_market_loss = expected_market_loss, 
			threshold_to_buy = r, 
			buy_amount = buy_amount, 
			price_per_share = price_per_share,
		)
		buy_at_bottom(capital_spent, pps)
		print()
