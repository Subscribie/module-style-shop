from flask import (Blueprint, request, render_template, abort, flash, url_for, 
    redirect)

from subscribie.auth import login_required
from subscribie import current_app
from jinja2 import TemplateNotFound
import tinycss
import yaml
from flask import Markup

module_style_shop = Blueprint('style_shop', __name__, template_folder='templates')

@module_style_shop.app_context_processor
def inject_custom_style():
  # Work out custom styling from jamla entry. 
	# Custom styling is applied by adding a "options->stlyes" entry
	# under the theme declaration.
	# Style entered will be injected into the base of the template
	# output as inline css using <style> tags.
	# 
  # Example valid entry:
	#
  # theme:
  # name: jesmond
  # options: 
  #   styles:
  #     - selector: body
  #       rules: 
  #         - color: red
  #         - background: orange
	#			- selector: .kcBlue
	#				rules:
	#					- background: black
	#					- border: 5px solid yellow;
  ruleSet = getCustomCSS()
  # Wrap style tags
  if ruleSet is not None:
    custom_css = ''.join(['<style type="text/css">', ruleSet, '</style>'])
    return dict(custom_css=custom_css)
  else:
    return dict()

def getCustomCSS():
  """Return css string of the defined custom css rules in Jamla.yaml"""
  # For naming conventions see:
  # https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/CSS_basics
  return ''
  if  jamla['theme']['options']['styles'] == []:
    return None # Exit if no custom styles defined

  ruleSets = ''
  for style in jamla['theme']['options']['styles']:
    declarations = ''
    selector = style['selector']
    for propertyValues in style['rules']:
      for cssProperty in propertyValues:
        declaration = "{cssProperty}: {propertyValue};".format(cssProperty=cssProperty, propertyValue=propertyValues[cssProperty])
      declarations += declaration
    # Wrap declarations with selector
    ruleSets += "{selector}{declarations}".format(selector=selector, declarations='{'+declarations+'}')
  return ruleSets

@module_style_shop.route('/style_shop/index') # Define a module index page
@module_style_shop.route('/style-shop')
@login_required
def style_shop():
  try:
    # Load custom css rules (if any) and display in an editable textbox
    customCSS = getCustomCSS()
    return render_template('show-custom-css.html', customCSS=customCSS)
  except TemplateNotFound:
    abort(404)

@module_style_shop.route('/style-shop', methods=['POST'])
@login_required
def save_custom_style():
  flash(Markup('Styling updated. View your <a href="/">updated shop</a>'))

  return redirect(url_for('style_shop.style_shop'))
  # Replace jamla->theme->options->styles with new css rulesets
  jamla['theme']['options']['styles'] = [] # Clear existing styles
  
  css = request.form['css']
  parser = tinycss.make_parser('page3')
  stylesheet = parser.parse_stylesheet(css)
  # Parse each rule, get its rulesets, declarations and save to jamla
  styles = []
  for ruleSet in stylesheet.rules:
    selector = ruleSet.selector.as_css()
    # Add selector to draftJamla
    rules = []
    for rule in ruleSet.declarations:
      cssProperty = rule.name
      propertyValue = rule.value.as_css()
      rules.append({cssProperty:propertyValue})
    styles.append({'selector':selector, 'rules': rules})
  # Append each style
  for style in styles:
    jamla['theme']['options']['styles'].append(style)

  fp = open(current_app.config["JAMLA_PATH"], "w")
  yaml.safe_dump(jamla, fp, default_flow_style=False)
  flash(Markup('Styling updated. View your <a href="/">updated shop</a>'))
    
  return redirect(url_for('style_shop.style_shop'))
