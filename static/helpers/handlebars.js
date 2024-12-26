/**
 * Here is a list of our Handlebars helpers
 * You can add or register new helper as your needs
 * For more information, read the docs here: https://handlebarsjs.com/guide/
 */

const Handlebars = require('handlebars/runtime');


/** How to pass Object?
 * > (object [name]=<value> [name]=<value> ...)
 * Example: {{#> partials/template.html person=(object name="steve" age=40 isPermitted=true) ... }}
 */
Handlebars.registerHelper('object', function ({ hash }) {
  return hash
})

/** How to pass Array?
 * > (array <value> <value> ...)
 * Example: {{#> partials/template.html persons=(array "steve" "john" "emily") ... }}
 */
Handlebars.registerHelper('array', function () {
  return Array.from(arguments).slice(0, arguments.length - 1)
})

/** How to use isDefined?
 * > isDefined [variableName]
 * Example: {{#if isDefined personName }}
 */
Handlebars.registerHelper('isDefined', function (value) {
  return value !== undefined
})

/** How to use ifEquals?
 * > ifEquals [variableName] <equalsValue>)
 * Example: {{#ifEquals personName "steve" }} ... {{/ifEquals}}
 */
Handlebars.registerHelper('ifEquals', function (arg1, arg2, options) {
  return (arg1 == arg2) ? options.fn(this) : options.inverse(this)
})


/** Export our Handlebars */
module.exports = Handlebars