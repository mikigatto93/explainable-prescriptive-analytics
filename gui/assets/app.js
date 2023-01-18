let socket = io();
let CLIENT_ID = null;

socket.on("socket:id", (id) => { console.log("New client id:" + id); CLIENT_ID = id; });