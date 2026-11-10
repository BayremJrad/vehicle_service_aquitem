const http = require('http');

const server = http.createServer(async (req, res) => {
  const method = req.method;
  const url = req.url.split('?')[0];

  // Initialize state
  let store = await pm.state.get('vehicles:store');
  let nextId = await pm.state.get('vehicles:nextId');

  if (!store || Object.keys(store).length === 0) {
    store = {
      1: { id: 1, nickName: 'The Lisa Marie', vin: '4M2DV11W4RDJ53329', make: 'Mercury', model: 'Villager', year: '1994', miles: 159864 },
      2: { id: 2, nickName: 'The Cube', vin: 'JN8AZ2KR1AT169594', make: 'Nissan', model: 'Cube', year: '2010', miles: 87432 }
    };
    await pm.state.set('vehicles:store', store);
  }

  if (!nextId || nextId < 3) {
    nextId = 3;
    await pm.state.set('vehicles:nextId', nextId);
  }

  const sendJSON = (statusCode, body) => {
    const payload = body === null ? '' : JSON.stringify(body);
    res.writeHead(statusCode, { 'Content-Type': 'application/json' });
    res.end(payload);
  };

  const readBody = () => new Promise((resolve, reject) => {
    let data = '';
    req.on('data', chunk => { data += chunk; });
    req.on('end', () => {
      try {
        resolve(data ? JSON.parse(data) : {});
      } catch (e) {
        reject(e);
      }
    });
    req.on('error', reject);
  });

  const vehicleIdMatch = url.match(/^\/vehicles\/(\d+)$/);

  try {
    // @endpoint POST /vehicles
    if (method === 'POST' && url === '/vehicles') {
      let body;
      try {
        body = await readBody();
      } catch (e) {
        return sendJSON(400, { message: 'Bad request body' });
      }

      const requiredFields = ['vin', 'make', 'model', 'year', 'miles'];
      for (const field of requiredFields) {
        if (body[field] === undefined || body[field] === null || body[field] === '') {
          return sendJSON(400, { message: `Request body missing required attribute: ${field}` });
        }
      }

      // VIN uniqueness check
      const currentStore = await pm.state.get('vehicles:store') || {};
      for (const v of Object.values(currentStore)) {
        if (v.vin === body.vin) {
          return sendJSON(409, { message: `Vehicle with VIN ${body.vin} already exists. Existing vehicle ID: ${v.id}` });
        }
      }

      const currentNextId = await pm.state.get('vehicles:nextId') || 3;
      const newVehicle = {
        id: currentNextId,
        nickName: body.nickName || '',
        vin: body.vin,
        make: body.make,
        model: body.model,
        year: body.year,
        miles: body.miles
      };

      currentStore[currentNextId] = newVehicle;
      await pm.state.set('vehicles:store', currentStore);
      await pm.state.set('vehicles:nextId', currentNextId + 1);

      return sendJSON(201, newVehicle);
    }

    // @endpoint GET /vehicles
    if (method === 'GET' && url === '/vehicles') {
      const currentStore = await pm.state.get('vehicles:store') || {};
      const vehicles = Object.values(currentStore);
      return sendJSON(200, vehicles);
    }

    // @endpoint GET /vehicles/:id
    if (method === 'GET' && vehicleIdMatch) {
      const id = parseInt(vehicleIdMatch[1], 10);
      const currentStore = await pm.state.get('vehicles:store') || {};
      const vehicle = currentStore[id];
      if (!vehicle) {
        return sendJSON(404, { message: `Vehicle with id: ${id} not found.` });
      }
      return sendJSON(200, vehicle);
    }

    // @endpoint PATCH /vehicles/:id
    if (method === 'PATCH' && vehicleIdMatch) {
      const id = parseInt(vehicleIdMatch[1], 10);
      const currentStore = await pm.state.get('vehicles:store') || {};
      const vehicle = currentStore[id];
      if (!vehicle) {
        return sendJSON(404, { message: `Vehicle with id: ${id} not found.` });
      }

      let body;
      try {
        body = await readBody();
      } catch (e) {
        return sendJSON(400, { message: 'Bad request body' });
      }

      if (!body || Object.keys(body).length === 0) {
        return sendJSON(400, { message: 'Bad request body' });
      }

      const updatedVehicle = { ...vehicle, ...body, id: vehicle.id };
      currentStore[id] = updatedVehicle;
      await pm.state.set('vehicles:store', currentStore);

      return sendJSON(200, updatedVehicle);
    }

    // @endpoint DELETE /vehicles/:id
    if (method === 'DELETE' && vehicleIdMatch) {
      const id = parseInt(vehicleIdMatch[1], 10);
      const currentStore = await pm.state.get('vehicles:store') || {};
      if (!currentStore[id]) {
        return sendJSON(404, { message: `Vehicle with id: ${id} not found.` });
      }

      delete currentStore[id];
      await pm.state.set('vehicles:store', currentStore);

      res.writeHead(204);
      return res.end();
    }

    // 404 fallback
    sendJSON(404, { message: 'Route not found' });

  } catch (err) {
    sendJSON(500, { message: 'Unexpected error' });
  }
});

server.listen(process.env.PORT || 3000);
