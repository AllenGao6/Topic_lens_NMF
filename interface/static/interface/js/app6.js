$(document).ready(function() {

  $.ajax({
    url: '/api_interface/get_init_cords/',
    type: 'post',
    success: function (xhr) {
      init_graph();
      get_cords(xhr['cords']);
      //console.log(xhr['filters']);
      get_doc_filter(xhr['filters'])
    },
    error: function(xhr) {
      if (xhr.status == 403) {
        Utils.notify('error', xhr.responseText);
      }
    }
  });

  /*$('#myChart').zingchart({
    data: {
      type: 'line',
      title: {
        text: 'Topic Comparisons',
        fontSize: 24,
      },
      legend: {
        draggable: true,
      },
      scaleX: {
        // Set scale label
        label: { text: 'Number of Topic' },
        // Convert text on scale indices
        labels: [ 2,4,6,8,10,12,14 ]
      },
      scaleY: {
        // Scale label with unicode character
        label: { text: 'Coherence Index' }
      },
      plot: {
        // Animation docs here:
        // https://www.zingchart.com/docs/tutorials/styling/animation#effect
        animation: {
          effect: 'ANIMATION_EXPAND_BOTTOM',
          method: 'ANIMATION_STRONG_EASE_OUT',
          sequence: 'ANIMATION_BY_NODE',
          speed: 275,
        }
      },
      series: [
        {
          // plot 1 values, linear data
          values: [23,20,27,29,25,17,15],
          text: 'LDA',
        },
        {
          // plot 2 values, linear data
          values: [35,42,33,49,35,47,35],
          text: 'NMF'
        },
        {
          // plot 2 values, linear data
          values: [15,22,13,33,44,27,31],
          text: 'CorEx'
        }
      ]
    }
  });*/
  

  allowDrop = function(ev) {
      ev.preventDefault();
  }

  drag = function(ev) {
      ev.dataTransfer.setData("text", ev.target.id);
  }

  drop = function(ev) {
      ev.preventDefault();
      var data = ev.dataTransfer.getData("text");
      // ev.target.parentNode.insertBefore(document.getElementById(data),ev.target);
      $(ev.target).closest(".content")[0].appendChild(document.getElementById(data));
  }

function saveJSON(data, filename){

    if(!data) {
        console.error('No data')
        return;
    }

    if(!filename) filename = 'console.json'

    if(typeof data === "object"){
        data = JSON.stringify(data, undefined, 4)
    }

    var blob = new Blob([data], {type: 'text/json'}),
        e    = document.createEvent('MouseEvents'),
        a    = document.createElement('a')

    a.download = filename
    a.href = window.URL.createObjectURL(blob)
    a.dataset.downloadurl =  ['text/json', a.download, a.href].join(':')
    
}

  // gen_json
  $('body').on("click", "#gen_json", function(){
    $.ajax({
      url: '/api_interface/gen_json/',
      type: 'post',
      data: {
      },
      success: function(xhr) {
        var cords = xhr['cords'];
        saveJSON(cords, 'cords.json');
        console.log(cords);
      },
      error: function(xhr) {
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  });

  // gen_json
  $('body').on("click", ".num-topics-2", function(){
    var topic_id = $(this).closest('.item').attr("topic-id");
    $(".show-petitions[topic-id=" + topic_id + "]").click();
  });

  // gen_json
  $('body').on("click", ".topic-container .delete", function(){
    var result = confirm("Want to delete the selected topic?");
    if (result) {
        $(this).closest('.topic-container').remove();
    }
    let topic_id = $(this).closest('.topic-container').attr('topic-id');
    $.ajax({
      url: '/api_interface/remove/',
      type: 'post',
      data: {
        "topic_id": topic_id,
      },
      success: function(xhr) {
        location.reload();
      },
      error: function(xhr) {
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  });

  // add new topic
  $('body').on("click", "#add-topic", function(){
    var new_topic_html = [
      '<div class="four wide column topic-container">',
        '<div class="ui card">',
          '<div class="content">',
            '<div class="header">',
                '<div class="ui mini input" style="width: 80%;">',
                  '<input class="topic-label" type="text" placeholder="Label..." topic-id="" value="New Label">',
                '</div>',
              '<input type="checkbox" class="topic-checkbox" style="float: right;">',
            '</div>',
          '</div>',
          '<div class="content topic-words" ondrop="drop(event)" ondragover="allowDrop(event)">  ',
            '<p></p>',
          '</div>',
          '<div class="extra content">',
            '<div class="ui mini button delete" data-inverted="" data-tooltip="delete this topic slot">',
              '<i class="trash icon"></i>',
              'Delete',
            '</div>',
          '</div>',
        '</div>',
      '</div>'
    ].join(' ');
    $("#topics-container").prepend(new_topic_html);
  });

  // move topic terms
  $('body').on("focusout", ".topic-label", function(){
    if($(this).attr("topic-id") != "") {
      var topic_label = $(this).val();
      var topic_id = $(this).attr("topic-id");
      $(".item[topic-id=" + topic_id + "] .child.checkbox label").text(topic_label);
    };
  });

  // move topic terms
  $('body').on("click", "#reallocation", function () {

    var new_labels = $(".topic-container .topic-label").map(function () {
      return $(this).val();
    }).get();
    var old_labels = $(".topic-container .topic-label").map(function () {
      return $(this).attr('value')
    }).get();
    //alert(new_labels+ " "+old_labels);
    
    var existsEmptyTopic = false;
    var existsEmptyTopicLabel = false;
    for (var i = 0; i < new_labels.length; i++){
      if (new_labels[i].replace(/\s/g, "") === "") {
        existsEmptyTopicLabel = true
      }
    }
    if (existsEmptyTopicLabel) {
      $(".warning").show();
        $(".warning .header").text('a topic label cannot be empty');
        setTimeout(function() {
          $('.warning').fadeOut('fast');
        }, 5000); // <-- time in milliseconds
      return;
    }
    $(".topic-words").each(function(){
      if ($(this).find(".label").length == 0) {
        $(".warning").show();
        $(".warning .header").text('a topic slot cannot be empty');
        setTimeout(function() {
          $('.warning').fadeOut('fast');
        }, 5000); // <-- time in milliseconds
        existsEmptyTopic = true;
      }
    });
    if (existsEmptyTopic) return;

    seconds = 0;
    loading = setInterval(function(){ myTimer() }, 1000);
    $.ajax({
      url: '/api_interface/update_topics_labels/',
      type: 'post',
      data: {
        'old_labels': old_labels.join("$-$"),
        'new_labels': new_labels.join("$-$"),
      },
      success: function (xhr) {
        location.reload();
      },
      error: function(xhr) {
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  });

  // split
  $('body').on("click", ".split-topic", function(){

    // window.scrollTo(0, 0);
    var $topic_container = $(this).closest(".topic-container");
    var num_split = $(this).siblings('input')[0].value;
    var origin_label = $topic_container.find('.topic-label').val();
    var words = get_words($topic_container);

    if (words.length <= num_split) {
      $(".warning").show();
      $(".warning .header").text('the number of topic words have to be larger than the number to split');
      setTimeout(function() {
        $('.warning').fadeOut('fast');
      }, 5000); // <-- time in milliseconds
      return;
    }

    if (num_split == 1) {
      $(".warning").show();
      $(".warning .header").text('The Split Number Cannot Be 1');
      setTimeout(function() {
        $('.warning').fadeOut('fast');
      }, 5000); // <-- time in milliseconds
      return;
    }

    if ($.isNumeric(num_split) && num_split > 0) {
      seconds = 0;
      loading = setInterval(function(){ myTimer() }, 1000);
      
      $.ajax({
        url: '/api_interface/split_topics_noupdate/',
        type: 'post',
        data: {
          'num_split': num_split,
          'words': words,
          'origin_label': origin_label,
        },
        success: function(xhr) {
          // $topic_container.remove();

          /*for (var i = num_split - 1; i >= 0 ; i--) {
          // add new topic
            var label = origin_label + ' -  -  - ' + i;
            var new_topic_html = [
              '<div class="four wide column topic-container">',
                '<div class="ui card">',
                  '<div class="content">',
                    '<div class="header">',
                        '<div class="ui mini input" style="width: 80%;">',
                          '<input class="topic-label" type="text" placeholder="Label..." topic-id="" value="' + label + '">',
                        '</div>',
                      '<input type="checkbox" class="topic-checkbox" style="float: right;">',
                    '</div>',
                  '</div>',
                  '<div class="content topic-words" ondrop="drop(event)" ondragover="allowDrop(event)">  ',
                    '<p></p>',
                  '</div>',
                  '<div class="extra content">',
                    '<div class="ui mini button delete" data-inverted="" data-tooltip="delete this topic slot">',
                      '<i class="trash icon"></i>',
                      'Delete',
                    '</div>',
                    '<div class="ui mini action input" style="width: 50%; float: right;">',
                      '<input type="text" style="width:3em;" placeholder="#">',
                      '<button class="split-topic ui mini button" topic-id="{{ forloop.counter0 }}" data-inverted="" data-tooltip="specify the number of topics to split">Split</button>',
                    '</div>',
                  '</div>',
                '</div>',
              '</div>'
            ].join(' ');
            $(new_topic_html).insertAfter($topic_container);
            for (var j = 0; j < xhr.word_set[i].length; j++) {
              $topic_container.next().find('.topic-words').append($("#word-" + xhr.word_set[i][j]));
            }
          }*/
          $("#topics-container").html(xhr['topics-container']);
          $("#topics-filters").html(xhr['topics-filters']);
          init_filters();
          init_graph();
          get_doc_filter(xhr['filters']);
          get_cords(xhr['cords']);
          window.scrollTo(0, 0);
        },
        error: function(xhr) {
          if (xhr.status == 403) {
            Utils.notify('error', xhr.responseText);
          }
        }
      });
    } else {
      $(".warning .header").text('Invalid number of spliting a topic');
    }
  });

  // merge
  $('body').on("click", "#merge", function(){

    // window.scrollTo(0, 0);
    var checked = $('.topic-checkbox:checkbox:checked');
    if(checked.length == 2) {

      // seconds = 0;
      // loading = setInterval(function(){ myTimer() }, 1000);

      var $topic_container_0 = $($('.topic-checkbox:checkbox:checked').closest(".topic-container")[0]);
      var $topic_container_1 = $($('.topic-checkbox:checkbox:checked').closest(".topic-container")[1]);
      var origin_label_0 = $topic_container_0.find('.topic-label').val();
      var origin_label_1 = $topic_container_1.find('.topic-label').val();
      var words = get_words($topic_container_0).concat(get_words($topic_container_1));

      var topic1_id = $(checked[0]).closest('.header').find(".topic-label").attr("topic-id");
      var topic2_id = $(checked[1]).closest('.header').find(".topic-label").attr("topic-id");

      var label = origin_label_0 + ' + ' + origin_label_1;
      var new_topic_html = [
        '<div class="four wide column topic-container">',
          '<div class="ui card">',
            '<div class="content">',
              '<div class="header">',
                  '<div class="ui mini input" style="width: 80%;">',
                    '<input class="topic-label" type="text" placeholder="Label..." topic-id="" value="' + label + '">',
                  '</div>',
                '<input type="checkbox" class="topic-checkbox" style="float: right;">',
              '</div>',
            '</div>',
            '<div class="content topic-words" ondrop="drop(event)" ondragover="allowDrop(event)">  ',
              '<p></p>',
            '</div>',
            '<div class="extra content">',
              '<div class="ui mini button delete" data-inverted="" data-tooltip="delete this topic slot">',
                '<i class="trash icon"></i>',
                'Delete',
              '</div>',
              '<div class="ui mini action input" style="width: 50%; float: right;">',
                '<input type="text" style="width:3em;" placeholder="#">',
                '<button class="split-topic ui mini button" topic-id="{{ forloop.counter0 }}" data-inverted="" data-tooltip="specify the number of topics to split">Split</button>',
              '</div>',
            '</div>',
          '</div>',
        '</div>'
      ].join(' ');
      $(new_topic_html).insertAfter($topic_container_0);
      for (var j = 0; j < words.length; j++) {
        $topic_container_0.next().find('.topic-words').append($("#word-" + words[j]));
      }
      $topic_container_0.remove();
      $topic_container_1.remove();
    } else {
      $(".warning .header").text('Merge requires [2] topics selected.');
    }
  });

  // highlight petitions
  $('body').on("click", ".show-petitions", function(){
    svg.selectAll(".dot")
      .attr("r",3.5) // reset size
      .classed({"not_possible":true,"selected":false}); // style as not possible

    var topic_id = $(this).attr("topic-id");

    var selected_doc_ids = []
    svg.selectAll(".dot")
      .filter(function(d) {
        if (d.topic_id == topic_id) {
          selected_doc_ids.push(d.doc_id);
        }
        return d.topic_id == topic_id
      })
      .classed({"not_possible":false,"possible":false})
      .attr("r",7);

    $("#docList .item").each(function(index) {
      var doc_id = $(this).attr('doc-idx');
      if (selected_doc_ids.length === 0 || selected_doc_ids.includes(doc_id)) {
        $(this).show();
      } else {
        $(this).hide();
      }
    });

    var docCount = $("#docList .item:visible").length;
    $("#numDocFound").text(docCount);
  });

  // hide/show petitions
  $('body').on("click", ".hide-petitions", function(){

    if ($.trim($(this).text()) == 'Hide') {
      $(this).text('Show');
      var newOpacity = 'hidden';
    } else {
      $(this).text('Hide');
      var newOpacity = 'visible';
    }

    svg.selectAll(".dot")
      .attr("r", 3.5) // reset size
      .classed({"not_possible":true,"selected":false}); // style as not possible

    var topic_id = $(this).attr("topic-id");

    var selected_doc_ids = []
    svg.selectAll(".dot")
      .filter(function(d) {
        if (d.topic_id == topic_id) {
          selected_doc_ids.push(d.doc_id);
        }
        return d.topic_id == topic_id
      })
      .classed({"not_possible":false,"possible":false})
      .attr("r",3.5)
      .attr("visibility", newOpacity);

    var docCount = $("#docList .item:visible").length;
    $("#numDocFound").text(docCount);
  });

  // undo
  $('body').on("click", "#undo", function(){
    window.scrollTo(0, 0);
    $.ajax({
      url: '/api_interface/last_state/',
      type: 'post',
      data: {
      },
      success: function(xhr) {
        $("#topics-container").html(xhr['topics-container']);
        $("#topics-filters").html(xhr['topics-filters']);
        init_filters();
        get_cords(xhr['cords']);
      },
      error: function(xhr) {
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  });

  // restart
  $('body').on("click", "#restart", function(){
    window.scrollTo(0, 0);
    $.ajax({
      url: '/api_interface/init_state/',
      type: 'post',
      data: {
      },
      success: function(xhr) {
        $("#topics-container").html(xhr['topics-container']);
        $("#topics-filters").html(xhr['topics-filters']);
        init_filters();
        get_cords(xhr['cords']);
      },
      error: function(xhr) {
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  });

  // show petitions
  $('body').on("click", ".show-only", function(){
    $("#hide-all").click();
    var topic_id = $(this).attr("topic-id");
    if($.trim($(".hide-petitions[topic-id='" + topic_id.toString() + "']").text()) === 'Show') {
      $(".hide-petitions[topic-id='" + topic_id.toString() + "']").click();
    }
  });

  // show all
  $('body').on("click", "#show-all", function(){
    for (var i = 0; i < $(".hide-petitions").length; i++) {
      if($.trim($(".hide-petitions[topic-id='" + i.toString() + "']").text()) === 'Show') {
        $(".hide-petitions[topic-id='" + i.toString() + "']").click();
      }
    }
  });

  // hide all
  $('body').on("click", "#hide-all", function(){
    for (var i = 0; i < $(".hide-petitions").length; i++) {
      if($.trim($(".hide-petitions[topic-id='" + i.toString() + "']").text()) === 'Hide') {
        $(".hide-petitions[topic-id='" + i.toString() + "']").click();
      }
    }
  });

  // change number of topics
  $('body').on("click", ".num-topics", function(){

    window.scrollTo(0, 0);
    var num_topics = $(this).siblings('input')[0].value;

    if ($.isNumeric(num_topics) && num_topics > 0) {

      seconds = 0;
      loading = setInterval(function(){ myTimer() }, 1000);

      $.ajax({
        url: '/api_interface/num_topics/',
        type: 'post',
        data: {
          'num_topics': num_topics,
        },
        success: function(xhr) {
          $("#topics-container").html(xhr['topics-container']);
          $("#topics-filters").html(xhr['topics-filters']);
          init_filters();
          init_graph();
          get_cords(xhr['cords']);
          get_doc_filter(xhr['filters'])
        },
        error: function(xhr) {
          if (xhr.status == 403) {
            // Utils.notify('error', xhr.responseText);
          }
        }
      });
    } else {
      $(".warning .header").text('Invalid number of spliting a topic');
    }
  });

  // click a document
  $('body').on("click", "#docList .item .header" ,function () {
    $("#docList .item .header").css("border", "");
    $(this).css("border", "1px solid");
    var $doc_container = $('#docDetail');
    var doc_idx = $(this).attr('doc-idx');
    get_doc($doc_container, doc_idx);
  });

  var get_topics = function(){
    var topics = []
    for (var i = 0; i < $(".topic-container").length; i++) {
      topics[i] = []
      var labels = $($(".topic-container")[i]).find(".label");
      for (var j = 0; j < labels.length; j++) {
        topics[i].push(labels[j].id.split('-')[1]);
      }
    }
    return JSON.stringify(topics);
  }

  var get_words = function($topic_container){
    var words = []
    var labels = $topic_container.find(".label");
    for (var j = 0; j < labels.length; j++) {
      words.push(labels[j].id.split('-')[1]);
    }
    return (words);
  }

var get_doc = function($doc_container, doc_idx){
    var labels = $(".topic-container .topic-label").map(function(){
      return $(this).val();
    }).get();
    $.ajax({
      url: '/api_interface/get_doc/',
      type: 'post',
      data: {
        'doc_idx': doc_idx,
        'labels': labels,
      },
      success: function(xhr) {
        $doc_container.find('._title').text(xhr.title);
        $doc_container.find('#rate_relevant').empty();
        $doc_container.find('._body').empty();
        $doc_container.find('._body').html(xhr.body);
        $doc_container.find('._signature_count').text(xhr.signature_count);
        $doc_container.find('._signature_threshold').text(xhr.signature_threshold);
        $doc_container.find('.q-topic').val(xhr.topic_accuracy);
        $doc_container.attr('doc-idx', doc_idx);


        // add topic names
        $doc_container.find('._topic_names').empty();
        if (xhr.label_list != "") {
          var colors = xhr.color_list.split(' ');
          var labels = xhr.label_list.split('^');
          for (var i = 0; i < colors.length; i++) {
            //var topic_id = topic_ids[i];
            //var topic_label = $(".item[topic-id=" + topic_id + "] .child.checkbox label").text();
            var label = '<a class="ui basic label" style="color:' + colors[i] + '">' + labels[i] + '</a>';
            $doc_container.find('._topic_names').append(label);
          }
        }
        
        //key words 
        $doc_container.find('._key_words').empty();
        if (xhr.keyword_list != "") {
          var keywords = xhr.keyword_list.split('^');
          for (var i = 0; i < keywords.length; i++) {
            items = keywords[i].split('~');
            //console.log(color, text);
            var label = '<a class="ui basic label" style="color:' + items[0] + '">' + items[1] + '</a>';
            $doc_container.find('._key_words').append(label);
          }
        }

        //relevant variable
        class1 = xhr.relevance == -1 ? 'class="ui red button active"' : 'class="ui button"';
        class2 = xhr.relevance == 0 ? 'class="ui blue button active"' : 'class="ui button"';
        class3 = xhr.relevance == 1 ? 'class="ui green button active"' : 'class="ui button"'
        
        not_relvance_html = '<button ' + class1 + ' tabindex="3" id="1" value="-1">Not Relevant</button><div class="or"></div>';
        no_info_html = '<button ' + class2 + ' tabindex="3" id="2" value="0">N/A</button><div class="or"></div>';
        relvance_html = '<button ' + class3 + ' tabindex="3" id="3" value="1">Relevant</button>';
        $doc_container.find('#rate_relevant').html(not_relvance_html+no_info_html+relvance_html);

        // sig progress
        $doc_container.find('.progress').progress({
          percent: xhr.sig_percent
        });
      },
      error: function(xhr) {
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  }

d3.scale.category30 = function() {
return d3.scale.ordinal().range(d3_category437);
};

// https://stackoverflow.com/questions/20847161/how-can-i-generate-as-many-colors-as-i-want-using-d3/46305307#46305307
var color_category30 = [
"d3fe14",
"1da49c",
"ccf6e9",
"a54509",
"7d5bf0",
"d08f5d",
"fec24c",
"0d906b",
"7a9293",
"7ed8fe",
"d9a742",
"c7ecf9",
"72805e",
"dccc69",
"86757e",
"a0acd2",
"fecd0f",
"4a9bda",
"bdb363",
"b1485d",
"b98b91",
"86df9c",
"6e6089",
"826cae",
"4b8d5f",
"8193e5",
"b39da2",
"5bfce4",
"df4280",
"a2aca6"
];

function d3_rgbString (value) {
  return d3.rgb(value >> 16, value >> 8 & 0xff, value & 0xff);
}

function get_cords(cords){
    var margin = {top: 20, right: 20, bottom: 30, left: 40},
        width = 1300 - margin.left - margin.right,
        height = 800 - margin.top - margin.bottom;

    var x = d3.scale.linear()
        .range([0, width]);

    var y = d3.scale.linear()
        .range([height, 0]);

    // var color = d3.scale.category20();
    var color = d3.scale.ordinal() // D3 Version 4
    .range(color_category30);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    $("#vis").empty();
    svg = d3.select("#vis").append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
      .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    clearInterval(loading);
    $("#loading").hide();
    $("#loading .text").text("Update complete.");
    // $(".warning .header").text('Update complete.');

    // Lasso functions to execute while lassoing
    var lasso_start = function() {
      lasso.items()
        .attr("r",3.5) // reset size
        .style("fill",null) // clear all of the fills
        .classed({"not_possible":true,"selected":false}); // style as not possible
    };

    var lasso_draw = function() {
      // Style the possible dots
      lasso.items().filter(function(d) {return d.possible===true})
        .classed({"not_possible":false,"possible":true});

      // Style the not possible dot
      lasso.items().filter(function(d) {return d.possible===false})
        .classed({"not_possible":true,"possible":false});
    };

    var lasso_end = function() {
      var selected_doc_ids = []
      // Reset the color of all dots
      lasso.items()
         .style("fill", function(d) { return color_category30[d.topic_id]; });

      // Style the selected dots
      lasso.items().filter(function(d) {
          var shouldShow = ($.trim($(".hide-petitions[topic-id='" + d.topic_id.toString() + "']").text()) === 'Hide');
          if (d.selected && shouldShow){
            selected_doc_ids.push(d['doc_id'])
          }
          return d.selected===true
        })
        .classed({"not_possible":false,"possible":false})
        .attr("r",7);

      // Reset the style of the not selected dots
      lasso.items().filter(function(d) {return d.selected===false})
        .classed({"not_possible":false,"possible":false})
        .attr("r",3.5);

      $("#docList .item").each(function(index) {
        var doc_id = $(this).attr('doc-idx');
        if (selected_doc_ids.length === 0 || selected_doc_ids.includes(doc_id)) {
          $(this).show();
        } else {
          $(this).hide();
        }
      });

      var docCount = $("#docList .item:visible").length;
      $("#numDocFound").text(docCount);

    };

    // Create the area where the lasso event can be triggered
    var lasso_area = svg.append("rect")
                          .attr("width",width)
                          .attr("height",height)
                          .style("opacity",0);
                          
    // Define the lasso
    var lasso = d3.lasso()
          .closePathDistance(75) // max distance for the lasso loop to be closed
          .closePathSelect(true) // can items be selected by closing the path?
          .hoverSelect(true) // can items by selected by hovering over them?
          .area(lasso_area) // area where the lasso can be started
          .on("start",lasso_start) // lasso start function
          .on("draw",lasso_draw) // lasso draw function
          .on("end",lasso_end); // lasso end function

    // Init the lasso on the svg:g that contains the dots
    svg.call(lasso);

    data = cords
    console.log(data);
    data.forEach(function(d) {
      d.cord_x = +d.cord_x;
      d.cord_y = +d.cord_y;
    });

    x.domain(d3.extent(data, function(d) { return d.cord_x; })).nice();
    y.domain(d3.extent(data, function(d) { return d.cord_y; })).nice();

    // svg.append("g")
    //     .attr("class", "x axis")
    //     .attr("transform", "translate(0," + height + ")")
    //     .call(xAxis)
    //   .append("text")
    //     .attr("class", "label")
    //     .attr("x", width)
    //     .attr("y", -6)
    //     .style("text-anchor", "end")
    //     .text("Sepal Width (cm)");

    // svg.append("g")
    //     .attr("class", "y axis")
    //     .call(yAxis)
    //   .append("text")
    //     .attr("class", "label")
    //     .attr("transform", "rotate(-90)")
    //     .attr("y", 6)
    //     .attr("dy", ".71em")
    //     .style("text-anchor", "end")
    //     .text("Sepal Length (cm)")

    svg.selectAll(".dot")
        .data(data)
      .enter().append("circle")
        .attr("id",function(d,i) {
          return "dot_" + i;}
        ) // added
        .attr("class", "dot")
        .attr("r", 3.5)
        .attr("cx", function(d) { return x(d.cord_x); })
        .attr("cy", function(d) { return y(d.cord_y); })
        .attr("topic-id", function (d) { return d.topic_name; })
        .attr("iden-index", function (d) { return d.topic_id; })
        .style("fill", function(d) { return d.color; })
        .on("mouseover", function(d) {
          //var label = $(".topic-container .topic-label[topic-id=" + d.topic_id + "]").val();
          var label = d.topic_name;
          $(".warning .header").html("Topic Label: " + label + '</br>' + "Doc Title: " + d.title + '</br></br>' + "Doc Content: " + d.body);
          $(".warning.message").show();
        }).on("mouseout", function(d) {
           $(".warning.message").hide();
        });

    lasso.items(d3.selectAll(".dot"));

    var num_topics = $(".topic-container").length;
    for (var i = 0; i < num_topics; i++) {
      var num_docs = $("circle[iden-index='" + (i).toString() + "']").length;
      // $(".topic-container .num-docs")[i].innerText = num_docs + " ";
      $(".item .num-topics-id")[i].innerText = num_docs;
    }

  }

  var seconds = 0;
  var el = document.getElementById('seconds-counter');
  var loading = setInterval(function(){ myTimer() }, 1000);

  function myTimer() {
      seconds += 1;
      $("#loading").show();
      $("#loading .text").text("Update in progress: " + seconds + " seconds...");
      // el.innerText = "Update in progress: " + seconds + " seconds...";
  }


  function init_filters(){

    $('.list .master.checkbox')
      .checkbox({
        // check all children
        onChecked: function() {
          var
            $childCheckbox  = $(this).closest('.checkbox').siblings('.list').find('.checkbox')
          ;
          $childCheckbox.checkbox('check');
          $("#show-all").click();
        },
        // uncheck all children
        onUnchecked: function() {
          var
            $childCheckbox  = $(this).closest('.checkbox').siblings('.list').find('.checkbox')
          ;
          $childCheckbox.checkbox('uncheck');
          $("#hide-all").click();
        }
      })
    ;

    $('.list .child.checkbox')
      .checkbox({
        // Fire on load to set parent value
        fireOnInit : true,
        // Change parent state on each child checkbox change
        onChange   : function() {

          var shouldShow = $(this).closest('.child.checkbox').checkbox("is checked");
          var topic_id = $(this).closest('.item').attr("topic-id");
          if (shouldShow) {
            if($.trim($(".hide-petitions[topic-id='" + topic_id.toString() + "']").text()) === 'Show') {
              $(".hide-petitions[topic-id='" + topic_id.toString() + "']").click();
            }
          } else {
            if($.trim($(".hide-petitions[topic-id='" + topic_id.toString() + "']").text()) === 'Hide') {
              $(".hide-petitions[topic-id='" + topic_id.toString() + "']").click();
            }
          }

          var
            $listGroup      = $(this).closest('.list'),
            $parentCheckbox = $listGroup.closest('.item').children('.checkbox'),
            $checkbox       = $listGroup.find('.checkbox'),
            allChecked      = true,
            allUnchecked    = true
          ;

          // check to see if all other siblings are checked or unchecked
          $checkbox.each(function() {
            if( $(this).checkbox('is checked') ) {
              allUnchecked = false;
            }
            else {
              allChecked = false;
            }
          });
          // set parent checkbox state, but dont trigger its onChange callback
          if(allChecked) {
            $parentCheckbox.checkbox('set checked');
          }
          else if(allUnchecked) {
            $parentCheckbox.checkbox('set unchecked');
          }
          else {
            $parentCheckbox.checkbox('set indeterminate');
          }
        }
      })
    ;

  }
  init_filters();

  // click tree node
  $("body").on('click', "#node_key", function(){
    var topic_id = $(this).find("p").text();
    seconds = 0;
    loading = setInterval(function(){ myTimer() }, 1000);
    
    $.ajax({
      url: '/api_interface/get_tree_node/',
      type: 'post',
      data: {
        'topic': topic_id,
      },
      success: function(xhr) {
        
        $("#topics-container").html(xhr['topics-container']);
        $("#topics-filters").html(xhr['topics-filters']);
        init_filters();
        init_graph();
        get_cords(xhr['cords']);
      },
      error: function (xhr) {
        alert("Please Select Non-leaf Topic");
        clearInterval(loading);
      $("#loading").hide();
      $("#loading .text").text("Update complete.");
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  });

  //check click for document filter
  $('body').on("click", "#doc_filt", function () {
    var topic_tag = $(this).find("a").text();
    var color = $(this).find("a").css("color");

    $.ajax({
      url: '/api_interface/doc_filter/',
      type: 'post',
      data: {
        'tag': topic_tag,
      },
      success: function(xhr) {
        $("#docList").empty();
        
        docs = xhr['docs']
        for (var i = 0; i < docs.length; i++){
          html = '<div class="item" doc-idx="' + docs[i]['idx'] + '" style="margin: 0.5em 0;"><a class="header" doc-idx="' + docs[i]['idx'] + '" topic-ids="' + docs[i]['topic_ids_str'] + '">' + docs[i]['title'] + '</a></div>';
          $("#docList").append(html);
        }
        var doc_num = docs.length.toString();
        $('#numDocFound').text(doc_num);
        $("#keyword_filters").empty()
        get_keyword_filter(xhr['keys'], color, topic_tag);
      },
      error: function (xhr) {
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  });

  //check click for key word filter
  $('body').on("click", "#key_filt", function () {
    var key_tag = $(this).find("a").text();
    alert('processing...');
  });

  //append element to doc filter
  function get_doc_filter(filters) {
    $("#doc_filters").empty();
    $("#keyword_filters").empty()
    var view_all = '<div id="doc_filt" ><a class="ui basic label" style="color: black">' + "View All" + '</a></div>';
    $("#doc_filters").append(view_all)
    for(var i = 1; i < filters.length; i++){
      var filter = '<div id="doc_filt" ><a class="ui basic label" style="color:' + filters[i][1] + '">' + filters[i][0] + '</a></div>';
      $("#doc_filters").append(filter)
    }
  }
  //append element to key word filter
  function get_keyword_filter(filters, color, topic) {
    $("#keyword_filters").empty();
    for(var i = 1; i < filters.length; i++){
      var filter = '<div id="key_filt" ><a class="ui basic label" topic="'+ topic + '" style="color:' + color + '">' + filters[i] + '</a></div>';
      $("#keyword_filters").append(filter)
    }
  }

  function init_graph() {

    $.ajax({
      url: '/api_interface/get_tree_graph/',
      type: 'post',
      data: {
        'a': "Apple",
        'b': "Tree",
      },
      success: function(xhr) {
        //console.log(typeof(xhr['tree']))
        //console.log(xhr['tree'])
        $("#OrganiseChart-simple").empty();
        html = new Treant( xhr['tree'] );
        $( "#OrganiseChart-simple" ).append(html);
        console.log("graph initialized!");
      },
      error: function(xhr) {
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  }

  function change_relev_button(index) {
    var $doc_container = $('#docDetail');
    $doc_container.find('#rate_relevant').empty();
    class1 = index == -1 ? 'class="ui red button active"' : 'class="ui button"';
    class2 = index == 0 ? 'class="ui blue button active"' : 'class="ui button"';
    class3 = index == 1 ? 'class="ui green button active"' : 'class="ui button"'
    
    not_relvance_html = '<button ' + class1 + ' tabindex="3" id="1" value="-1">Not Relevant</button><div class="or"></div>';
    no_info_html = '<button ' + class2 + ' tabindex="3" id="2" value="0">N/A</button><div class="or"></div>';
    relvance_html = '<button ' + class3 + ' tabindex="3" id="3" value="1">Relevant</button>';
    $doc_container.find('#rate_relevant').html(not_relvance_html+no_info_html+relvance_html);
  }
  
  //clicked not relevant button
  $("body").on('click', "#1", function () {
    var rele_value = $(this).attr('value');
    var doc_index = $(this).closest(".doc-container").attr('doc-idx')
    $.ajax({
      url: '/api_interface/set_relev_index/',
      type: 'post',
      data: {
        'doc_index': doc_index,
        'relevance': rele_value,
      },
      success: function (xhr) {
        change_relev_button(-1);
      },
      error: function (xhr) {
        alert("Error Occured");
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  });

  //clicked no info button
  $("body").on('click', "#2", function () {
    var rele_value = $(this).attr('value');
    var doc_index = $(this).closest( ".doc-container" ).attr('doc-idx')
    $.ajax({
      url: '/api_interface/set_relev_index/',
      type: 'post',
      data: {
        'doc_index': doc_index,
        'relevance': rele_value,
      },
      success: function (xhr) {
        change_relev_button(0);
      },
      error: function(xhr) {
        if (xhr.status == 403) {
          Utils.notify('error', xhr.responseText);
        }
      }
    });
  });

  //clicked relevant button
    $("body").on('click', "#3", function () {
      var rele_value = $(this).attr('value');
      var doc_index = $(this).closest(".doc-container").attr('doc-idx')
      $.ajax({
        url: '/api_interface/set_relev_index/',
        type: 'post',
        data: {
          'doc_index': doc_index,
          'relevance': rele_value,
        },
        success: function (xhr) {
          change_relev_button(1);
        },
        error: function (xhr) {
          if (xhr.status == 403) {
            Utils.notify('error', xhr.responseText);
          }
        }
      });
    });
    
});

