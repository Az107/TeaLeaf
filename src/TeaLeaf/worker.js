class Store {
  constructor(store_id) {
    this.store_id = store_id;
    this.base_url = "/api/_store/" + store_id;
  }

  async _apiCall(method, id, body) {
    let config = {
      method: method,
    };
    let url = this.base_url;
    if (id != undefined) {
      url = url + "/" + id;
    }
    if (body != undefined) {
      config.body = typeof body == "string" ? body : JSON.stringify(body);
    }
    let result = await fetch(url, config);
    window.location.reload();
    return result;
  }
  async suscribe(callback) {}
  async set(id, data) {
    await this._apiCall("POST", id, data);
  }
  async update(id, data) {
    await this._apiCall("PATCH", id, data);
  }
  async get(id) {
    await this._apiCall("GET", id);
  }
}

function fetchAndUpdate(url, config, elementId) {
  {
    console.log(elementId);
    console.log({ config });
    config = JSON.parse(config);
    if (config.headers == undefined) {
      config.headers = {};
    }
    if (config.body) {
      config.body = JSON.stringify(config.body);
      config.headers["Content-Type"] = "application/json";
    }
    console.log({ config });
    fetch(url, config)
      .then((response) => response.text())
      .then((text) => (document.getElementById(elementId).innerHTML = text))
      .catch((err) => {
        {
          console.log({ err });
        }
      });
  }
}
