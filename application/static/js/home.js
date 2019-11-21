
        window.id = 1;
        window.energy_levels = ['Low Energy', 'Moderate Energy', 'High Energy'];
        window.fitness_levels = ['Beginner', 'Intermediate', 'Advanced'];
        window.selected_list = ['Beginner', 'Moderate Energy'];

        function hover(element) {
          element.setAttribute('src', '/static/images/' + element.name + 'Hover.png');
          element.style.transition = "box-shadow .3s ease-in-out";
        }

        function unhover(element) {
          element.setAttribute('src', '/static/images/' + element.name + '.png');
        }

        function hoverSelection(element) {
          element.style.transition = "transform .15s ease-in-out, box-shadow .3s ease-in-out";
          element.style.transform = "scale(1.5)";
        }

        function unhoverSelection(element) {
          element.style.transform = "scale(1)";
        }


        function updateSelected(id, string) {

            document.getElementById("error_selected").style.display = "none";

            if (document.getElementById(id).checked == true) {

                if (document.getElementById(id).type == "radio") {

                    if (window.fitness_levels.indexOf(string) != -1) {

                        if (window.selected_list.indexOf(string) == -1) {
                            window.selected_list.unshift(string);

                            for (i = 0; i < window.fitness_levels.length; i++) {
                              if (window.fitness_levels[i] == string) {
                                continue;
                              } else {
                                if (window.selected_list.indexOf(window.fitness_levels[i]) > -1) {
                                    window.selected_list.splice(window.selected_list.indexOf(window.fitness_levels[i]), 1);
                                }
                              }
                            }

                            document.getElementById("selected").innerHTML = window.selected_list.join("<br>")
                            return;
                        } else {
                            return;
                        }

                    } else {

                        if (window.selected_list.indexOf(string) == -1) {
                            window.selected_list.splice(1, 0, string);

                            for (i = 0; i < window.energy_levels.length; i++) {
                              if (window.energy_levels[i] == string) {
                                continue;
                              } else {
                                if (window.selected_list.indexOf(window.energy_levels[i]) > -1) {
                                    window.selected_list.splice(window.selected_list.indexOf(window.energy_levels[i]), 1);
                                }
                              }
                            }

                            document.getElementById("selected").innerHTML = window.selected_list.join("<br>")
                            return;
                        } else {
                            return;
                        }
                    }
                }

                if (window.selected_list.length >= 17) {
                    document.getElementById("error_selected").style.display = "block";
                    document.getElementById(id).checked = false;
                    return;
                }

                window.selected_list.push(string);
                document.getElementById("selected").innerHTML = window.selected_list.join("<br>")
            } else {
                window.selected_list.splice(window.selected_list.indexOf(string), 1);
                document.getElementById("selected").innerHTML = window.selected_list.join("<br>")
            }
        }

        function nextOption() {

          if (window.id == 4) {
            return;
          }

          window.id = window.id + 1

          if (window.id == 4) {
            document.getElementById('next').setAttribute('src', '/static/images/arrowDisabled.png');
          } else {
            document.getElementById('next').setAttribute('src', '/static/images/arrow.png');
            document.getElementById('prev').setAttribute('src', '/static/images/arrow.png');
          }

          var i;
          var x = document.getElementsByClassName("option");
          for (i = 0; i < x.length; i++) {
            x[i].style.display = "none";
            x[i].setAttribute('src', '/static/images/arrow.png');
          }
          document.getElementById(window.id).style.display = "block";

        }

        function prevOption() {

          if (window.id == 1) {
            return;
          }

          window.id = window.id - 1;

          if (window.id == 1) {
            document.getElementById('prev').setAttribute('src', '/static/images/arrowDisabled.png');
          } else {
            document.getElementById('prev').setAttribute('src', '/static/images/arrow.png');
            document.getElementById('next').setAttribute('src', '/static/images/arrow.png');
          }

          var i;
          var x = document.getElementsByClassName("option");
          for (i = 0; i < x.length; i++) {
            x[i].style.display = "none";
            x[i].setAttribute('src', '/static/images/arrow.png')
          }
          document.getElementById(window.id).style.display = "block";

        }
