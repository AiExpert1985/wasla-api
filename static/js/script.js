let gates = true;
document.querySelector('#consider-gates').addEventListener("change", (event)=> gates = event.target.checked);

let drivers_file;
let drivers;
document.querySelector('#drivers').addEventListener("change", (event) => {
    drivers_file = event.target.files;
    let drivers_reader = new FileReader();
    drivers_reader.readAsBinaryString(drivers_file[0]);
    drivers_reader.onload = (event)=>{
        let drivers_data = event.target.result;
        let drivers_workbook = XLSX.read(drivers_data,{type:"binary"});
        let drivers_rowObject = XLSX.utils.sheet_to_row_object_array(drivers_workbook.Sheets[drivers_workbook.SheetNames[0]]);
        drivers = JSON.stringify(drivers_rowObject,undefined,4);
    }
});

let students_file;
let students;
document.querySelector('#students').addEventListener("change", (event) =>{
    students_file = event.target.files;
    let students_reader = new FileReader();
    students_reader.readAsBinaryString(students_file[0]);
    students_reader.onload = (event)=>{
        let students_data = event.target.result;
        let students_workbook = XLSX.read(students_data,{type:"binary"});
        let students_rowObject = XLSX.utils.sheet_to_row_object_array(students_workbook.Sheets[students_workbook.SheetNames[0]]);
        students = JSON.stringify(students_rowObject,undefined,4);
     }
});

document.querySelector('#post').addEventListener("click", () => {
    let data = {"drivers": drivers,
                "students": students,
                "consider_gates": gates,
                "api_key": "ksdjf34234a23423",
                "center_coords": [43.146406822212754, 36.37665963355008]
    };
    fetch('/algorithm', {
      method: 'POST',
      headers: {
        'Content-Type': "application/json; charset=UTF-8"
      },
      body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => console.log('Success:', result))
    .catch((error) => console.error('Error:', error));
});


function initMap() {
  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 11,
    center: { lat: 36.37665963355008, lng: 43.146406822212754 },
    mapTypeId: "roadmap",
  });
  const flightPlanCoordinates = [
    { lat: 36.3081484, lng: 43.1983524 },
    { lat: 36.3114923, lng: 43.1918611 },
    { lat: 36.3672184, lng: 43.1349632 },
    { lat: 36.3766596, lng: 43.1464068 },
  ];
  const flightPath = new google.maps.Polyline({
    path: flightPlanCoordinates,
    geodesic: true,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 1.0,
  });

  flightPath.setMap(map);
 const flight2PlanCoordinates = [
    { lat: 36.3081484, lng: 43.2983524 },
    { lat: 36.3114923, lng: 43.2918611 },
    { lat: 36.3672184, lng: 43.2349632 },
    { lat: 36.3766596, lng: 43.2464068 },
  ];
  const flight2Path = new google.maps.Polyline({
    path: flight2PlanCoordinates,
    geodesic: true,
    strokeColor: "#FF0000",
    strokeOpacity: 1.0,
    strokeWeight: 1.0,
  });

  flight2Path.setMap(map);
}





