function getUrl() {
  var url = window.location.href;
  document.getElementById("current url").value = url;
  document.getElementById("whats share").href = "https://api.whatsapp.com/send?phone=&text=" + url;
}
window.addEventListener('load', getUrl); // for call getUrl function on load

function copyClipboard() {

  var copyText = document.getElementById("current url"); // Get the text field

  copyText.select(); // Select the text field

  copyText.setSelectionRange(0, 99999); // For mobile devices

  document.execCommand("copy");
}
