let drivers_file;
let students_file;
let drivers = [];
let students;
let input_drivers;
let selected_drivers = [];
let daily;
let gates = true;
let daily_drivers = [];
let current_day = "";
let stats;
let week_days;
let show_only_selected = false;
let arabic_week_days = {sa: "السبت", su:"الاحد", mo:"الاثنين", tu:"الثلاثاء", we:"الاربعاء", th:"الخميس"}

document.querySelector('#consider-gates').addEventListener("change", (event)=>
    gates = event.target.checked);
document.querySelector('.show-selected-only').addEventListener("change", (event)=>
    show_only_selected = event.target.checked);

function reset_algorithm(){
    selected_drivers = [];
    daily_drivers = []
    initMap();
    document.querySelector(".driver-checkboxes").hidden = true;
    document.querySelector(".save").hidden = true;
    document.querySelector(".stats").hidden = true;
    let drivers_parent = document.querySelector(".select-drivers");  // remove children of this element
    while (drivers_parent.firstChild) {
        drivers_parent.removeChild(drivers_parent.firstChild);
    }
}


function initMap() {
    let icon_base = "https://developers.google.com/maps/documentation/javascript/examples/full/images/";
    const map = new google.maps.Map(document.getElementById("map"), {
                                    zoom: 11,
                                    center: { lat: 36.3766596335, lng: 43.14640682224 },
                                    mapTypeId: "roadmap",
                                    });
    let to_plot_drivers;
    if(show_only_selected){
        to_plot_drivers = selected_drivers;
    }
    else{
        to_plot_drivers = drivers;
    }

    for(let i=0; i<to_plot_drivers.length; i++){
        // show driver locations
        let driver_lat = to_plot_drivers[i]["coords"]["lat"];
        let driver_lng = to_plot_drivers[i]["coords"]["lng"];
        driver_lng = driver_lng + 0.0015* Math.random()
        let driver_marker = new google.maps.Marker({
                position: {"lat": driver_lat, "lng": driver_lng},
                map,
//                icon: "static/images/car_marker.png",
        });

        // display info when clicking driver icon
        let driver_students = to_plot_drivers[i]['students']
        let students_info = "<p> ------------------------------- </p>";
        for(let k=0; k<driver_students.length; k++){
            students_info += '<p dir="rtl"> الطالب : &nbsp' + driver_students[k]['name'] + '</p>'
        }
        const driver_info =
            '<div class="icon-info" dir="rtl">' +
                    '<h2 id="firstHeading" class="firstHeading">' + to_plot_drivers[i]['name'] + '</h1>' +
                    '<div id="bodyContent">' +
                        '<p dir="rtl"> الصفة : &nbsp سائق</p>' +
                        '<p dir="rtl"> المنطقة : &nbsp' + to_plot_drivers[i]['district'] + '</p>' +
                        '<p dir="rtl"> المسافة : &nbsp' + to_plot_drivers[i]['dist'] + ' &nbsp كم </p>' +
                        '<p dir="rtl"> هاتف : &nbsp' + to_plot_drivers[i]['phone'] + '</p>' +
                        students_info +
                     "</div>" +
            "</div>";
        const driver_info_window = new google.maps.InfoWindow({
            content: driver_info,
          });
        driver_marker.addListener("click", () => {
            // remove previous info box - this was created by me ?
            let info_div = document.querySelector(".icon-info");
            if (info_div != null){
                let parent = info_div.parentNode.parentNode.parentNode.parentNode.parentNode;
                parent.remove();
            }
            driver_info_window.open({
              anchor: driver_marker,
              map,
              shouldFocus: false,
            });
         });
        // show student locations for each driver
        let students = to_plot_drivers[i].students;
        for(let j=0; j<students.length; j++){
            if (current_day !== ""){
                students[j]["driver"] = students[j][current_day];
            }
            let student_lat = students[j]["coords"]["lat"];
            let student_lng = students[j]["coords"]["lng"];
            student_lat = student_lat + 0.0002* Math.random()
            student_lng = student_lng + 0.002* Math.random()
            let student_marker = new google.maps.Marker({
                                    position: {"lat": student_lat, "lng": student_lng},
                                    map,
                                    icon: icon_base + "library_maps.png",
                            });
            // display info when clicking student icon
            const student_info =
                '<div class="icon-info" dir="rtl">' +
                        '<h2 id="firstHeading" class="firstHeading">' + students[j]['name'] + '</h1>' +
                        '<div id="bodyContent">' +
                            '<p dir="rtl"> الصفة : &nbsp طالب</p>' +
                            '<p dir="rtl"> المنطقة : &nbsp' + students[j]['district'] + '</p>' +
                            '<p dir="rtl"> البوابة : &nbsp' + students[j]['gate_name'] + '</p>' +
                            '<p dir="rtl"> هاتف : &nbsp' + students[j]['phone'] + '</p>' +
                            '<p> ------------------------------- </p>' +
                            '<p dir="rtl"> السائق : &nbsp' + students[j]['driver'] + '</p>' +
                         "</div>" +
                "</div>";
            const student_info_window = new google.maps.InfoWindow({
                content: student_info,
              });
            student_marker.addListener("click", () => {
                // remove previous info box - this was created by me ?
                let info_div = document.querySelector(".icon-info");
                if (info_div != null){
                    let parent = info_div.parentNode.parentNode.parentNode.parentNode.parentNode;
                    parent.remove();
                }
                student_info_window.open({
                  anchor: student_marker,
                  map,
                  shouldFocus: true,
                });
             });
        }
        driver_marker.setMap(map)
    }
    if(selected_drivers.length>0){
        for(let i=0; i<selected_drivers.length; i++){
            let random_color = '#'+(0x1000000+(Math.random())*0xffffff).toString(16).substr(1,6);
            let path_coordinates = selected_drivers[i]["path"];
            let driver_path = new google.maps.Polyline({
                path: path_coordinates,
                geodesic: true,
                strokeColor: random_color,
                strokeOpacity: 2.0,
                strokeWeight: 2.0,
            });
            driver_path.setMap(map)
        }
    }
}


function add_stats(stats) {
    document.querySelector(".stats").hidden = false;
    let ids = ["#gate-stats", "#distance-stats", "#short-long-dist", "#drivers-students"];
    let groups = [['one_gate', 'two_gates', 'more_gates'],
                  ['total_distance', 'average_distance'],
                  ['shorted_distance', 'longest_distance'],
                  ['num_drivers_without_students', 'num_drivers_not_full']];
    for (let i = 0; i < ids.length; i++){
        let main_div = document.querySelector(ids[i]);
        main_div.innerHTML = ""
        for (let j=0; j<groups[i].length; j++){
            let key = groups[i][j];
            let div = document.createElement("div");
            div.innerHTML = stats[key];
            main_div.appendChild(div);
        }
    }
}

// create a side list of all drivers, so that it can be displayed/hidden on the map
function create_drivers_list(){
    document.querySelector(".driver-checkboxes").hidden = false;
    document.querySelector(".save").hidden = false;
    document.querySelector(".all-drivers").checked = true;
    if(daily === false){
        document.querySelector(".week-days").hidden = true;
    }
    let main_div = document.querySelector(".select-drivers");
    for(let i = 0; i < selected_drivers.length; i++){
        let name = selected_drivers[i]["name"];
        let div = document.createElement("div")
        main_div.appendChild(div)
        let label = document.createElement("label");
        label.innerHTML = name;
        let checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.id = name;
        checkbox.value = name;
        checkbox.name = name;
        checkbox.dataset.idx = `${i}`;
        checkbox.className += "select-driver";
        checkbox.checked = true;
        div.appendChild(checkbox);
        div.appendChild(label);
    }
}

function add_week_days(){
    document.querySelector(".driver-checkboxes").hidden = false;
    document.querySelector(".save").hidden = false;
    document.querySelector(".all-drivers").checked = true;
    document.querySelector(".week-days").hidden = false;
    document.querySelectorAll('.drivers-week-day').forEach(item => {
        item.hidden = !week_days.includes(item.dataset.day); // show only valid days
        item.addEventListener('click', event => {
        reset_algorithm();
        let selected_element = event.target;
        let nextSibling = selected_element.parentNode.firstElementChild;
        while(nextSibling) {
            nextSibling.style.color = "white";
            nextSibling = nextSibling.nextElementSibling;
        }
          selected_element.style.color = "yellow";
        let chosen_day = selected_element.dataset.day;
        daily_drivers = [];
        for(let i = 0; i < drivers.length; i++){
                let driver = drivers[i];
                document.querySelector(".stats").hidden = false;
                driver["students"] = driver[chosen_day]["students"];
                driver["path"] = driver[chosen_day]["path"];
                current_day = chosen_day;
                daily_drivers.push(driver);
            }
        selected_drivers = daily_drivers;
        add_stats(stats[chosen_day]);
        create_drivers_list();
        initMap();
      });
    });

}

// select drivers to be displayed on the map
document.querySelector('.select-drivers').addEventListener("change", ()=> {
        let checkboxes = document.querySelectorAll(".select-driver");
        let num_checkboxes = checkboxes.length;
        let selections = [num_checkboxes]
        checkboxes.forEach(element => {
            let idx = element.dataset.idx
            selections[idx] = element.checked;
    });
    selected_drivers = []
    let drivers_list = drivers;
    if(daily){
        drivers_list = daily_drivers;
    }
    for(let i=0; i<drivers_list.length; i++){
        if(selections[i] === true){
            selected_drivers.push(drivers_list[i]);
        }
    }
    initMap(selected_drivers);

    document.querySelector(".all-drivers").checked = selected_drivers.length === drivers.length;
});


// select or deselect all drivers
document.querySelector('.select-groups').addEventListener("change", ()=> {
    let is_all_drivers = document.querySelector(".all-drivers").checked;
    let checkboxes = document.querySelectorAll(".select-driver");
    if(is_all_drivers){
        selected_drivers = drivers;
        checkboxes.forEach(element => element.checked = true)
    }
    else {
        selected_drivers = [];
        checkboxes.forEach(element => element.checked = false);
    }
    initMap();
});


// upload drivers excel file
document.querySelector('#upload-drivers').addEventListener("change", (event) => {
    drivers_file = event.target.files;
    let drivers_reader = new FileReader();
    drivers_reader.readAsBinaryString(drivers_file[0]);
    drivers_reader.onload = (event)=>{
        let drivers_data = event.target.result;
        let drivers_workbook = XLSX.read(drivers_data,{type:"binary"});
        let drivers_rowObject = XLSX.utils.sheet_to_row_object_array(drivers_workbook.Sheets[drivers_workbook.SheetNames[0]]);
        input_drivers = JSON.stringify(drivers_rowObject,undefined,4);
        input_drivers = JSON.parse(input_drivers);
        if(input_drivers[0]["leave_time"]){
            document.querySelector('#upload-drivers-label').innerHTML = "Wrong Drivers File !";
        } else {
            document.querySelector('#upload-drivers-label').innerHTML = "Drivers File Uploaded";
        }
    }
});


// upload students excel file
document.querySelector('#upload-students').addEventListener("change", (event) =>{
    students_file = event.target.files;
    let students_reader = new FileReader();
    students_reader.readAsBinaryString(students_file[0]);
    students_reader.onload = (event)=>{
        let students_data = event.target.result;
        let students_workbook = XLSX.read(students_data,{type:"binary"});
        let students_rowObject = XLSX.utils.sheet_to_row_object_array(students_workbook.Sheets[students_workbook.SheetNames[0]]);
        students = JSON.stringify(students_rowObject,undefined,4);
        students = JSON.parse(students);
        if(students[0]["leave_time"]){
            document.querySelector('#upload-students-label').innerHTML = "Students File Uploaded";
        } else {
            document.querySelector('#upload-students-label').innerHTML = "Wrong Students File !";
        }
     }


});


// send json data to server
document.querySelector('#post').addEventListener("click", () => {
    reset_algorithm()
    // first clear previous created elements if there are any
    let children = document.querySelector(".stats").children;
    for(let i=0; i<children.length; i++){
        children[i].innerHTML = "";
    }
    document.querySelector(".select-drivers").innerHTML = "";
    let api_key = document.querySelector("#key").value;
    let data = {"drivers": input_drivers,
                "students": students,
                "consider_gates": gates,
                "api_key": api_key,
                "center_coords": [43.146406822212754, 36.37665963355008]
    };
    students = []
    drivers = [];
    selected_drivers = [];
    fetch('/eshtirakat/algorithm/data', {
      method: 'POST',
      headers: {
        'Content-Type': "application/json; charset=UTF-8"
      },
      body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(result => {
        daily = result["daily"];
        if(daily){
            week_days = result['week_days'];
            students = result['students'];
            drivers = result['drivers'];
            stats = result['stats'];
            add_week_days();
            console.log(students);
            console.log(drivers);
        }
        else{
            stats = result['stats'];
            drivers = result['drivers'];
            selected_drivers = drivers;
            initMap();
            add_stats(stats);
            create_drivers_list();
        }

     })
    .catch((error) => console.error('Error:', error));
});


// save weekly eshtirak to excel
function json_to_array_weekly(drivers){
    let drivers_arr = [];
    let column_titles = ["ت", "اسم الطالب", "المنطقة", "x", "y", "وقت الخروج", "رقم البوابة", "اسم البوابة",
                         "رقم الطالب", "الاصدقاء", "اسم الكابتن", "x", "y", "المنطقة", "المسافة", "المدة", "رقم الكابتن"]
    drivers_arr.push(column_titles);
    for(let i=0; i<drivers.length; i++){
        let driver_name = drivers[i]["name"];
        let driver_coords = drivers[i]["coords"];
        let driver_distance = drivers[i]["dist"];
        let driver_district = drivers[i]["district"];
        let driver_phone = drivers[i]["phone"];
        let students = drivers[i]["students"];
        for(let j=0; j<4; j++){
            if(j >= students.length){drivers_arr.push([
                                      (i*4)+j+1,
                                      "","","","","","","","","",
                                      driver_name,
                                      driver_coords["lng"],
                                      driver_coords["lat"],
                                      driver_district,
                                      driver_distance,
                                      "",
                                      driver_phone,
                                      ]);
            }
            else{drivers_arr.push([
                              (i*4)+j+1,
                              students[j]["name"],
                              students[j]["district"],
                              students[j]["coords"]["lng"],
                              students[j]["coords"]["lat"],
                              "",
                              students[j]["gate_group"],
                              students[j]["gate_name"],
                              students[j]["phone"],
                              "",
                              driver_name,
                              driver_coords["lng"],
                              driver_coords["lat"],
                              driver_district,
                              driver_distance,
                              "",
                              driver_phone,
                              ]);
            }
        }
    }
    return(drivers_arr);
}


// function json_to_student_array_daily(students){
//     let students_arr = [];
//     let column_titles = ["id", "name", "district", "x", "y", "leave_time", "gate_group", "gate_name",
//                          "phone", "friends", "sa", "su", "mo", "tu", "we", "th"]
//     students_arr.push(column_titles);
//     for(let i=0; i<students.length; i++){
//         students_arr.push([
//                           i,
//                           students[i]["name"],
//                           students[i]["district"],
//                           students[i]["coords"]["lng"],
//                           students[i]["coords"]["lat"],
//                           "",
//                           students[i]["gate_group"],
//                           students[i]["gate_name"],
//                           students[i]["phone"],
//                           "",
//                           students[i]["sa"],
//                           students[i]["su"],
//                           students[i]["mo"],
//                           students[i]["tu"],
//                           students[i]["we"],
//                           students[i]["th"],
//                           ]);
//     }
//     return(students_arr);
// }

function json_to_student_array_daily(students){
    let students_arr = [];
    let column_titles = ["ت", "اسم الطالب", "المنطقة", "x", "y", "وقت الخروج", "رقم البوابة", "اسم البوابة",
        "رقم الطالب", "الاصدقاء", "اليوم", "اسم الكابتن", "رقم الكابتن", "المنطقة"]
    students_arr.push(column_titles);
    for(let i=0; i<students.length; i++){
        for(let j=0; j<week_days.length; j++){
            let day = week_days[j];
            students_arr.push([
                i+1,
                students[i]["name"],
                students[i]["district"],
                students[i]["coords"]["lng"],
                students[i]["coords"]["lat"],
                "",
                students[i]["gate_group"],
                students[i]["gate_name"],
                students[i]["phone"],
                "",
                arabic_week_days[day],
                students[i][day]["name"],
                students[i][day]["phone"],
                students[i][day]["loc"],
            ]);
        }
    }
    return(students_arr);
}


function json_to_driver_array_daily(drivers){
    let drivers_arr = [];
    let column_titles = ["ت", "الكابتن", "x", "y", "المنطفة", "المسافة", "المدة", "رقم الكابتن","اليوم" , "اسم الطالب", "رقم الطالب", "المنطقة", "x", "y", "وقت الخروج", "رقم البوابة", "اسم البوابة",
                          "الاصدقاء"]
    drivers_arr.push(column_titles);
    for(let i=0; i<drivers.length; i++){
        let driver_name = drivers[i]["name"];
        let driver_coords = drivers[i]["coords"];
        let driver_distance = drivers[i]["dist"];
        let driver_district = drivers[i]["district"];
        let driver_phone = drivers[i]["phone"];
        for (let k=0; k<week_days.length; k++){
            let day = week_days[k]
            let students = drivers[i][day]["students"];
            for(let j=0; j<4; j++){
                if(j >= students.length){drivers_arr.push([
                    i+1,
                    driver_name,
                    driver_coords["lng"],
                    driver_coords["lat"],
                    driver_district,
                    driver_distance,
                    "",
                    driver_phone,
                    arabic_week_days[day],
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    ]);
                }
                else{drivers_arr.push([
                    i+1,
                    driver_name,
                    driver_coords["lng"],
                    driver_coords["lat"],
                    driver_district,
                    driver_distance,
                    "",
                    driver_phone,
                    arabic_week_days[day],
                    students[j]["name"],
                    students[j]["phone"],
                    students[j]["district"],
                    students[j]["coords"]["lng"],
                    students[j]["coords"]["lat"],
                    "",
                    students[j]["gate_group"],
                    students[j]["gate_name"],
                    "",
                    ]);
                }
            }
        }
    }
    return(drivers_arr);
}


function s2ab(s) {
    let buf = new ArrayBuffer(s.length);
    let view = new Uint8Array(buf);
    for (let i=0; i<s.length; i++) view[i] = s.charCodeAt(i) & 0xFF;
    return buf;
}


function save_excel(){
    let wb = XLSX.utils.book_new();
    if(daily){
            wb.SheetNames.push("Drivers");
            wb.SheetNames.push("Students");
            let students_arr = json_to_student_array_daily(students);
            wb.Sheets["Students"] = XLSX.utils.aoa_to_sheet(students_arr);
            let drivers_arr = json_to_driver_array_daily(drivers);
            wb.Sheets["Drivers"] = XLSX.utils.aoa_to_sheet(drivers_arr);
	    }
	else{
	        wb.SheetNames.push("Drivers");
            let result_arr = json_to_array_weekly(drivers);
            wb.Sheets["Drivers"] = XLSX.utils.aoa_to_sheet(result_arr);
	}
    let wbout = XLSX.write(wb, {bookType:'xlsx',  type: 'binary'});
    saveAs(new Blob([s2ab(wbout)],{type:"application/octet-stream"}), 'students_matched.xlsx');
}

document.querySelector(".save-button").addEventListener("click", () => save_excel());
