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
