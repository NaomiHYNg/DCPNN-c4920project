        function openWorkout(workoutName) {
          var i;
          var x = document.getElementsByClassName("workout");
          for (i = 0; i < x.length; i++) {
            x[i].style.display = "none";
          }
          document.getElementById(workoutName).style.display = "block";
        }
        function checkCompleted() {
            var checkboxes = document.forms.check_complete.elements;
            var incomplete = []
            for (var i = 0; i < checkboxes.length; i++) {
                if (checkboxes[i].checked) {
                    continue;
                } else {
                    incomplete.push(checkboxes[i].getAttribute("name"))
                }
            }
            if (incomplete.length == 0) {
                document.getElementById("check_complete").submit();
            } else {
                document.getElementById("finish_workout").style.display = "block";
                document.getElementById("finish_workout").innerHTML = "FOLLOWING EXERCISES NOT COMPLETED:<br>";
                for (i = 0; i < incomplete.length; i++) {
                    document.getElementById("finish_workout").innerHTML = document.getElementById("finish_workout").innerHTML + "- " + incomplete[i] + "<br>";
                }
            }
        }