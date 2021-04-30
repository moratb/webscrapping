var config = {
  baseBet: { value: 1000, type: 'balance', label: 'base bet' },
  payout: { value: 10, type: 'multiplier' },
  stop: { value: 16, type: 'multiplier', label: 'stop if counter >' },
  loss: {
    value: 'increase', type: 'radio', label: 'On Loss',
    options: {
      increase: { value: 1.111, type: 'multiplier', label: 'Multipy bet by' },
    }
  },
  win: {
    value: 'base', type: 'radio', label: 'On Win',
    options: {
      base: { type: 'noop', label: 'Return to base bet' }
    }
  }
};


log('Script is running..');
var counter = 1;
var currentBet = config.baseBet.value;
engine.on('GAME_STARTING', onGameStarted);
engine.on('GAME_ENDED', onGameEnded);

function onGameStarted() {
 log('Current counter is: ', counter);
 if (counter <= config.stop.value) {
   log('betting NOW!');
   engine.bet(roundBit(currentBet), config.payout.value);
 } else {
   log('counter TOO HIGH:',counter, ' NOT BETTING');
 }
}

function onGameEnded() {
  var lastGame = engine.history.first();

  // IF WE DIDN'T BET
  if (!lastGame.wager) {
    if (lastGame.bust < config.payout.value) {
      counter += 1;
      log('last game bust below', config.payout.value, 'so next counter is:',counter);
    } else {
      counter = 1;
      log('last game bust above', config.payout.value, 'so next counter is:',counter);
      currentBet = config.baseBet.value;
    }
    return;
  }

  // IF WE WON
  if (lastGame.cashedAt) {
    currentBet = config.baseBet.value;
    counter = 1;
    log('We won, so next bet will be', currentBet/100, 'bits ROUNDED UP');
  } else {
    // IF WE LOST
    counter += 1;
    console.assert(config.loss.value === 'increase');
    currentBet *= config.loss.options.increase.value;
    log('We lost, so next bet will be', currentBet/100, 'bits ROUNDED UP');
  }

}


function roundBit(bet) {
  return Math.ceil(bet / 100) * 100;
}
