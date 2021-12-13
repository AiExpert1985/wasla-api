document.addEventListener('DOMContentLoaded', function(){
    document.querySelector(".stats").hidden = true;
    document.querySelector(".select-drivers").hidden = true;
    var drivers;
    var selected_drivers;
});

function initMap(paths) {
    const map = new google.maps.Map(document.getElementById("map"), {
                                    zoom: 11,
                                    center: { lat: 36.3766596335, lng: 43.14640682224 },
                                    mapTypeId: "roadmap",
                                    });
    for(var i in paths){
        var random_color = '#'+(0x1000000+(Math.random())*0xffffff).toString(16).substr(1,6)
        const student_coordinates = paths[i]
        const driver_path = new google.maps.Polyline({
                                path: student_coordinates,
                                geodesic: true,
                                strokeColor: random_color,
                                strokeOpacity: 1.0,
                                strokeWeight: 1.0,
                                });
        driver_coordinates = student_coordinates[0]
        new google.maps.Marker({
            position: driver_coordinates,
            map,
            label: i,
        });
        driver_path.setMap(map)
    }
}


function add_stats(stats) {
    document.querySelector(".stats").hidden = false;
    document.querySelector(".select-drivers").hidden = false;
    var ids = ["#gate-stats", "#distance-stats", "#short-long-dist"];
    var groups = [['one_gate', 'two_gates', 'more_gates'],
                  ['total_distance', 'average_distance'],
                  ['shorted_distance', 'longest_distance']];
    for (var i = 0; i < ids.length; i++){
        var main_div = document.querySelector(ids[i]);
        for (var j=0; j<groups[i].length; j++){
            var key = groups[i][j];
            var div = document.createElement("div");
            div.innerHTML = stats[key];
            main_div.appendChild(div);
        }
    }
}

function add_drivers(){
    var main_div = document.querySelector(".select-drivers")
    for(var i = 0; i < drivers.length; i++){
        name = drivers[i]["name"];
        var div = document.createElement("div")
        main_div.appendChild(div)
        var label = document.createElement("label");
        label.innerHTML = name;
        var checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.id = name;
        checkbox.value = name;
        checkbox.name = name;
        checkbox.dataset.idx = i;
        checkbox.className += "select-driver";
        checkbox.checked = true;
        div.appendChild(checkbox);
        div.appendChild(label);
    }
}

document.querySelector('.select-drivers').addEventListener("change", (event)=> {
        var checkboxes = document.querySelectorAll(".select-driver");
        var num_checkboxes = checkboxes.length;
        var selections = [num_checkboxes]
        checkboxes.forEach(element => {
        var idx = element.dataset.idx
        var checked = element.checked;
        selections[idx] = checked;
    });
    selected_drivers = []
    for(var i=0; i<drivers.length; i++){
        if(selections[i] == true){
            selected_drivers.push(drivers[i]);
        }
    }
    console.log(selected_drivers);
});


let gates = true;
document.querySelector('#consider-gates').addEventListener("change", (event)=> gates = event.target.checked);

let drivers_file;
let input_drivers;
document.querySelector('#drivers').addEventListener("change", (event) => {
    drivers_file = event.target.files;
    let drivers_reader = new FileReader();
    drivers_reader.readAsBinaryString(drivers_file[0]);
    drivers_reader.onload = (event)=>{
        let drivers_data = event.target.result;
        let drivers_workbook = XLSX.read(drivers_data,{type:"binary"});
        let drivers_rowObject = XLSX.utils.sheet_to_row_object_array(drivers_workbook.Sheets[drivers_workbook.SheetNames[0]]);
        input_drivers = JSON.stringify(drivers_rowObject,undefined,4);
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
    let data = {"drivers": input_drivers,
                "students": students,
                "consider_gates": gates,
                "api_key": "ksdjf34234a23423",
                "center_coords": [43.146406822212754, 36.37665963355008]
    };
    fetch('/algorithm/data', {
      method: 'POST',
      headers: {
        'Content-Type': "application/json; charset=UTF-8"
      },
      body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => {
        paths = result['paths']
        stats = result['stats']
        drivers = result['drivers']
        console.log(drivers)
        initMap(paths)
        add_stats(stats)
        add_drivers(drivers)
     })
    .catch((error) => console.error('Error:', error));
});










