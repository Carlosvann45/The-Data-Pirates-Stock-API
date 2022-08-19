const fs = require('fs/promises');
const express = require('express');
const cors = require('cors');

const app = express();

app.get('/stock/data/quote', (request, response) => {
  // TODO: add code to get parameters for stocks to grab

  // TODO: add code to open websocket and get selected stock inforamtion

  // TODO: close socket and return information found
});

app.listen(3000);
