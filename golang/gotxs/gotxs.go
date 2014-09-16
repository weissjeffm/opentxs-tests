// vim: tw=0
package gotxs

/*
This could become a thin wrapper around the opentxs library in Go.
*/


/*
At the moment, the paths below need to be set for each system where this
is compiled (-Iinclude and -L/usr/local/lib64). This can be fixed with
cmake integration
*/

/*
#cgo CXXFLAGS: -std=c++11 -Iinclude -DEXPORT=
#cgo LDFLAGS: -L/usr/local/lib64  -lopentxs-client -lopentxs-ext -lopentxs-basket -lopentxs-cash -lopentxs-core -lstdc++
*/
import "C"

import "fmt"

func main() {
    fmt.Println("Hello World!")
}
