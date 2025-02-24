function fetchAndUpdate(url, config, elementId) {
  {
    console.log({ config });
    config = JSON.parse(config);
    if (config.body) {
      config.body = JSON.stringify(config.body);
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
