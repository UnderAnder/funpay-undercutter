# Funpay-undercutter

Undercutting game currency offers at https://funpay.ru

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Support](#support)
- [Contributing](#contributing)
- [License](#license)

## Requirements

* python (3.8+)

## Installation

```sh
git clone https://github.com/UnderAnder/funpay-undercutter.git
cd funpay-undercutter
python setup.py install
```

## Usage

### Basic:
```sh
funpay-undercutter <"Game with region">
```
```sh
> funpay-undercutter "World of Warcraft RU, EU"
  
  ===== World of Warcraft RU, EU =====
1. Update data
2. Undercut all offers
3. Change offer
0. Exit
```

### Undercutting the price of all your offers every 10 minutes:

Setup cookie with system variables: FUNPAY_PHPSESSID, FUNPAY_GOLDEN

 * MacOS, GNU/Linux:
    ```sh
    export FUNPAY_PHPSESSID = "<YOUR PHPSESSID>"
    export FUNPAY_GOLDEN = "<YOUR GOLDEN_KEY>"
    ```

Setup cron task:
```sh
> crontab -e
>> */10 * * * * funpay-undercutter "World of Warcraft RU, EU" -a
```

## Support

Please [open an issue](https://github.com/UnderAnder/funpay-undercutter/issues/new) for support.

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). 
Create a branch, add commits, and [open a pull request](https://github.com/UnderAnder/funpay-undercutter/compare/).

## License

GNU GPLv3. See [LICENSE](https://github.com/UnderAnder/funpay-undercutter/blob/master/LICENSE) for the full details. 