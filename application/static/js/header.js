    function openSavedWorkout(workoutName) {
      var i;
      var x = document.getElementsByClassName("savedWorkout");
      for (i = 0; i < x.length; i++) {
        x[i].style.display = "none";
      }
      document.getElementById(workoutName).style.display = "block";
    }

    function deleteWorkout(id) {

        var input = document.createElement("input");

        input.setAttribute("type", "hidden");

        input.setAttribute("name", "delete_id");

        input.setAttribute("value", id);

        document.getElementById("delete_saved_workout").appendChild(input);
        document.getElementById('delete_saved_workout').submit();

        return
    }