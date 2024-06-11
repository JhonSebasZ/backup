<?php
/*
*Plugin Name: plugin prueba
*Version: 0.1
*Plugin URI: ${TM_PLUGIN_BASE}
*Description:
*Author: Jhon Sebastian Zuñiga
*Author URI: ${TM_HOMEPAGE}
*/

function js_badges_menu(){
    add_options_page( 'js badges plugin', 'js badges', 'manage_options', 'js-badges', 'js_badges_options_page' );
}

add_action( 'admin_menu', 'js_badges_menu');

function js_badges_options_page(){
    if(!current_user_can('manage_options')){
        wp_pie('you do not have sufficient permissions to access this page');
    }
    echo '<p>
        Welcome to our plugin page!
    </p>'
}

