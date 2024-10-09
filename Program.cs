using System;

namespace MiaAutomate
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length == 3)  // Verificamos que se hayan recibido 3 parámetros
            {
                try
                {
                    // Convertimos el primer argumento a un entero (ContactID)
                    int contactID = int.Parse(args[0]);

                    // Asignamos los otros dos argumentos directamente (Plantilla y Query)
                    string plantilla = args[1];
                    string query = args[2];

                    // Imprimimos los valores
                    Console.WriteLine("ContactID: " + contactID);
                    Console.WriteLine("Plantilla: " + plantilla);
                    Console.WriteLine("Query: " + query);
                }
                catch (FormatException)
                {
                    Console.WriteLine("El primer parámetro debe ser un número entero.");
                }
            }
            else
            {
                Console.WriteLine("Se deben proporcionar exactamente 3 parámetros: ContactID (int), Plantilla (string), y Query (string).");
            }
        }
    }
}