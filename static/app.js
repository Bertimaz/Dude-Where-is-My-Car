$('form input[type="file"]').change(event => {
  let arquivos = event.target.files;
  if (arquivos.length === 0) {
    console.log('sem imagem pra mostrar')
  } else {
      if(arquivos[0].type == 'image/jpeg') {
        $('img').remove();
        let imagem = $('<img class="img-fluid">');
        imagem.attr('src', window.URL.createObjectURL(arquivos[0]));
        $('figure').prepend(imagem);
      } else {
        alert('Formato não suportado')
      }
  }
});

navigator.geolocation.getCurrentPosition(showCoordinates, errors);

var htmlLatitude = document.getElementById("latitude");
var htmlLongitude = document.getElementById("longitude");
var htmlGeoError = document.getElementById("geoLocationError");

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showCoordinates, errors);
    } else {
       alert("Geolocation is not supported by this browser");
    }
}


function showCoordinates(myposition) {

    htmlLatitude.value=myposition.coords.latitude;
    htmlLongitude.value=myposition.coords.longitude;
    geoLocationError.value=0;


}

function errors(err){
    if(err.code==1){
        geoLocationError.value=1;
        alert("Libere o acesso a localização")
    }
    else{
        geoLocationError.value=2;
        alert("Geolocation error");
    }

    }
