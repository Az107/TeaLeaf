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
    await fetch_front();
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

async function fetch_front() {
  let result = await fetch(window.location.href);
  if (result.ok) {
    let serverHtml = await result.text();
    let vdom = new DOMParser().parseFromString(serverHtml, "text/html");
    authority_zero(vdom.body, document.body);
  }
}

function authority_zero(a, b) {
  if (a.children == undefined) {
    b.innerHTML = a.innerHTML;
    return;
  }
  for (const [vdom, dom] of zip(a.children, b.children)) {
    if (vdom.id.startsWith("tlmg")) continue;
    if (vdom.innerHTML == dom.innerHTML) continue;
    if (vdom.children.length == 0) {
      dom.innerHTML = vdom.innerHTML;
    } else {
      authority_zero(vdom, dom);
    }
  }
  if (a.children.length > b.children.length) {
    //add elements
    for (let i = b.children.length; i < a.children.length; i++) {
      b.appendChild(a.children[i]);
    }
  } else if (a.children.length < b.children.length) {
    for (let i = b.children.length; i > a.children.length; i--) {
      b.removeChild(b.children[i]);
    }
  }
}

function* zip(a, b) {
  const len = Math.min(a.length, b.length);

  for (let i = 0; i < len; i++) {
    yield [a[i], b[i]];
  }
}

/**
 * Returns a hash code from a string
 * @param  {String} str The string to hash.
 * @return {Number}    A 32bit integer
 * @see http://werxltd.com/wp/2010/05/13/javascript-implementation-of-javas-string-hashcode-method/
 */
function hashCode(str) {
  let hash = 0;
  for (let i = 0, len = str.length; i < len; i++) {
    let chr = str.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
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
